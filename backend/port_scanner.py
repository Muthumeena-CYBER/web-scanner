"""
Full TCP port scanner module.
Uses Python socket + ThreadPoolExecutor (no external scanners).
"""

import ipaddress
import logging
import socket
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse

LOGGER = logging.getLogger("scanner.port_scanner")

TOTAL_PORTS = 65535
CONNECT_TIMEOUT_SECONDS = 0.75
MAX_WORKERS = 300

SAFETY_WARNING = "Unauthorized port scanning is illegal. Use only on systems you own."

SERVICE_MAP = {
    20: "FTP Data",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    111: "RPCBind",
    135: "MS RPC",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    465: "SMTPS",
    587: "SMTP Submission",
    993: "IMAPS",
    995: "POP3S",
    1433: "MSSQL",
    1521: "Oracle DB",
    2049: "NFS",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    6379: "Redis",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
    9200: "Elasticsearch",
    27017: "MongoDB",
}

DB_PORTS = {3306, 1433, 5432, 6379, 27017}
REMOTE_ACCESS_PORTS = {22, 23, 3389, 5900}
WEB_PORTS = {80, 443, 8080}


def extract_hostname(target: str) -> str:
    """Accept URL/domain/IP and return hostname."""
    if not target:
        raise ValueError("Target is required")

    candidate = target.strip()
    parsed = urlparse(candidate if "://" in candidate else f"http://{candidate}")
    hostname = parsed.hostname or parsed.path
    hostname = (hostname or "").strip().strip("/")

    if not hostname:
        raise ValueError("Could not extract hostname from input")

    return hostname


def resolve_hostname(hostname_or_url: str) -> tuple[str, str]:
    """Resolve input to normalized hostname + IPv4/IPv6 string."""
    hostname = extract_hostname(hostname_or_url)
    try:
        ip_address = socket.gethostbyname(hostname)
        return hostname, ip_address
    except socket.gaierror as exc:
        raise ValueError(f"Failed to resolve hostname '{hostname}': {exc}") from exc


def _is_local_or_test_target(hostname: str) -> bool:
    lowered = hostname.lower()

    if lowered in {"localhost", "::1"}:
        return True

    try:
        ip_obj = ipaddress.ip_address(lowered)
        if ip_obj.is_loopback:
            return True
    except ValueError:
        pass

    test_markers = (
        ".local",
        ".test",
        ".localhost",
        ".example",
        "test.",
        "dev.",
        "staging.",
        "sandbox.",
        "qa.",
        "uat.",
    )
    return any(marker in lowered for marker in test_markers)


def is_scan_allowed(hostname_or_url: str, authorization_confirmed: bool = False) -> bool:
    """Allow scanning only for authorized targets or local/test targets."""
    hostname = extract_hostname(hostname_or_url)
    return bool(authorization_confirmed) or _is_local_or_test_target(hostname)


def guess_service(port: int) -> str:
    return SERVICE_MAP.get(port, "Unknown Service")


def classify_port_risk(port: int) -> str:
    if port in DB_PORTS:
        return "High"
    if port in REMOTE_ACCESS_PORTS:
        return "Medium"
    return "Low"


def summarize_port_risk(open_ports: list[int], unknown_ports: list[int]) -> str:
    open_set = set(open_ports)
    if open_set.intersection(DB_PORTS):
        return "High"
    if open_set.intersection(REMOTE_ACCESS_PORTS):
        return "Medium"
    if len(unknown_ports) > 10:
        return "Medium"
    if open_set and open_set.issubset(WEB_PORTS):
        return "Low"
    if not open_set:
        return "Low"
    return "Medium"


def _scan_single_port(ip_address: str, port: int) -> dict | None:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(CONNECT_TIMEOUT_SECONDS)
            result = sock.connect_ex((ip_address, port))
            if result == 0:
                return {
                    "port": port,
                    "service_guess": guess_service(port),
                    "risk": classify_port_risk(port),
                }
    except (socket.timeout, OSError):
        return None
    return None


def scan_all_ports(hostname: str, progress_callback=None) -> dict:
    """
    Scan all TCP ports (1..65535) for a host/url.
    Returns JSON-ready dict in required format.
    """
    normalized_hostname, ip_address = resolve_hostname(hostname)
    LOGGER.info("Starting full TCP scan for host=%s ip=%s", normalized_hostname, ip_address)

    open_ports = []
    scanned_count = 0
    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for result in executor.map(
                lambda p: _scan_single_port(ip_address, p),
                range(1, TOTAL_PORTS + 1),
            ):
                scanned_count += 1
                if result:
                    open_ports.append(result)
                if progress_callback and (scanned_count % 1000 == 0 or scanned_count == TOTAL_PORTS):
                    try:
                        progress_callback(scanned_count, TOTAL_PORTS, len(open_ports))
                    except Exception:
                        # Never fail the scan because of UI progress callback issues.
                        pass
    except Exception as exc:
        LOGGER.exception("Port scan error for %s: %s", normalized_hostname, exc)
        raise

    open_ports.sort(key=lambda item: item["port"])
    open_port_numbers = [entry["port"] for entry in open_ports]
    unknown_ports = [port for port in open_port_numbers if guess_service(port) == "Unknown Service"]
    risk_summary = summarize_port_risk(open_port_numbers, unknown_ports)

    LOGGER.info(
        "Completed full TCP scan for host=%s open_ports=%s risk=%s",
        normalized_hostname,
        len(open_ports),
        risk_summary,
    )

    return {
        "target_host": normalized_hostname,
        "target_ip": ip_address,
        "total_ports_scanned": TOTAL_PORTS,
        "open_ports_count": len(open_ports),
        "open_ports": open_ports,
        "risk_summary": risk_summary,
        "safety_warning": SAFETY_WARNING,
    }
