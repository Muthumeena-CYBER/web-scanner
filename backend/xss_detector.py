import html
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import requests

from xss_payloads import XSS_PAYLOADS

def _contains_reflection(text: str, payload: str) -> bool:
    if not text:
        return False
    if payload in text:
        return True
    if html.escape(payload) in text:
        return True
    encoded = urlencode({"x": payload}).split("=", 1)[1]
    if encoded in text:
        return True
    return False

def test_xss(url: str, custom_payloads=None):
    """
    Returns list of tuples: (param, payload, 'Reflected XSS')
    Tests reflected XSS via GET query parameters.
    Supports custom payloads for enhanced testing.
    """
    findings = []
    try:
        parts = urlsplit(url)
        query_pairs = parse_qsl(parts.query, keep_blank_values=True)

        if not query_pairs:
            return findings

        # Use custom payloads if provided, otherwise use defaults
        payloads = custom_payloads if custom_payloads else XSS_PAYLOADS

        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; xss-scanner/1.0)"
        }

        for i, (param, _) in enumerate(query_pairs):
            for payload in payloads:
                mutated = list(query_pairs)
                mutated[i] = (param, payload)
                new_query = urlencode(mutated, doseq=True)
                mutated_url = urlunsplit((parts.scheme, parts.netloc, parts.path, new_query, parts.fragment))
                try:
                    resp = requests.get(mutated_url, headers=headers, timeout=10)
                except requests.RequestException:
                    continue

                ctype = resp.headers.get("Content-Type", "")
                body = resp.text or ""
                if ("text/html" in ctype or "<html" in body.lower()) and _contains_reflection(body, payload):
                    findings.append((param, payload, "Reflected XSS"))
                    break  # stop after first hit for this param
        return findings
    except Exception:
        return findings