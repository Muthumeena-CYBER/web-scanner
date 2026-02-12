import requests
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from payloads import ERROR_BASED_PAYLOADS, BOOLEAN_PAYLOADS, TIME_BASED_PAYLOADS

ERROR_SIGNATURES = [
    # Generic
    "sql syntax", "syntax error", "sqlstate", "sql exception", "database error",
    # MySQL
    "you have an error in your sql syntax", "warning: mysql", "mysql_fetch", "mysqli",
    "you have an error in your sql syntax; check the manual that corresponds to your mysql server version for the right syntax to use near",
    # PostgreSQL
    "pg_query", "psql:", "postgresql", "fatal error",
    # SQL Server
    "microsoft sql server", "odbc sql server driver", "unclosed quotation mark",
    # Oracle
    "ora-", "oracle",
    # SQLite
    "sqlite error", "sqlite3",
    # Common
    "unknown column", "invalid column", "near"
]

def _build_url(parts, pairs):
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(pairs, doseq=True), parts.fragment))

def _safe_get(url, headers, timeout=10):
    try:
        return requests.get(url, headers=headers, timeout=timeout)
    except requests.RequestException:
        return None

def test_sqli(url: str, custom_payloads=None):
    """
    Returns list of tuples: (param, payload, sqli_type)
    Tries error-based, boolean-based, and time-based SQL injection via GET query parameters.
    Supports custom payloads for error-based detection.
    """
    findings = []
    parts = urlsplit(url)
    query_pairs = parse_qsl(parts.query, keep_blank_values=True)

    if not query_pairs:
        return findings

    headers = {"User-Agent": "Mozilla/5.0 (compatible; sqli-scanner/1.0)"}

    # Use custom payloads if provided, otherwise use defaults
    error_payloads = custom_payloads if custom_payloads else ERROR_BASED_PAYLOADS
    error_payloads = [payload for payload in error_payloads if isinstance(payload, str) and payload]
    if not error_payloads:
        error_payloads = ERROR_BASED_PAYLOADS

    # Baseline response for comparison
    baseline_resp = _safe_get(url, headers)
    baseline_time = baseline_resp.elapsed.total_seconds() if baseline_resp else None

    for i, (param, _) in enumerate(query_pairs):
        # 1) Error-based
        for payload in error_payloads:
            mutated = list(query_pairs)
            mutated[i] = (param, payload)
            test_url = _build_url(parts, mutated)
            resp = _safe_get(test_url, headers)
            if not resp or not resp.text:
                continue
            body_lower = resp.text.lower()
            if any(sig in body_lower for sig in ERROR_SIGNATURES):
                findings.append((param, payload, "Error-based SQLi"))
                break  # stop after first hit for this param

        # 2) Boolean-based (compare true vs false)
        true_payload = BOOLEAN_PAYLOADS.get("true")
        false_payload = BOOLEAN_PAYLOADS.get("false")
        if true_payload and false_payload:
            mutated_true = list(query_pairs); mutated_true[i] = (param, true_payload)
            mutated_false = list(query_pairs); mutated_false[i] = (param, false_payload)

            url_true = _build_url(parts, mutated_true)
            url_false = _build_url(parts, mutated_false)

            resp_true = _safe_get(url_true, headers)
            resp_false = _safe_get(url_false, headers)

            if resp_true and resp_false:
                len_true = len(resp_true.text or "")
                len_false = len(resp_false.text or "")
                status_differs = resp_true.status_code != resp_false.status_code
                # Consider significant difference in body sizes or status codes
                size_diff = abs(len_true - len_false)
                threshold = max(200, int(0.3 * max(len_true, len_false, 1)))
                if status_differs or size_diff >= threshold:
                    findings.append((param, f"{true_payload} | {false_payload}", "Boolean-based SQLi"))

        # 3) Time-based (measure delay vs baseline)
        if baseline_time is not None:
            for payload in TIME_BASED_PAYLOADS:
                mutated = list(query_pairs); mutated[i] = (param, payload)
                test_url = _build_url(parts, mutated)
                resp = _safe_get(test_url, headers, timeout=12)
                if not resp:
                    continue
                elapsed = resp.elapsed.total_seconds()
                # If server delayed notably (e.g., >= 3s more than baseline), flag
                if elapsed - baseline_time >= 3.0:
                    findings.append((param, payload, "Time-based SQLi"))
                    break  # stop after first hit for this param

    return findings
