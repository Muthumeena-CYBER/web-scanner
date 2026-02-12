import requests
from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup
import re
import warnings

# Suppress BeautifulSoup markup warnings
warnings.filterwarnings('ignore', category=UserWarning, module='bs4')

def test_csrf(url: str, crawled_urls: list = None):
    """
    Returns list of tuples: (form_name, vulnerability_type, severity, details)
    Tests for CSRF vulnerabilities by checking:
    - Missing CSRF tokens
    - Weak/predictable tokens
    - Missing SameSite cookie attribute
    - Missing referer checks
    """
    findings = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; csrf-scanner/1.0)"
        }
        
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return findings
        
        # Validate response content before parsing
        if not resp.text or len(resp.text.strip()) < 10:
            return findings
        
        # Check if content-type is HTML
        content_type = resp.headers.get('content-type', '').lower()
        if content_type and 'html' not in content_type:
            return findings
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Check for forms
        forms = soup.find_all('form')
        if not forms:
            return findings
        
        # Check for CSRF token in forms
        findings.extend(_check_csrf_tokens(forms, url))
        
        # Check for SameSite cookie attribute
        findings.extend(_check_samesite_cookies(resp.headers, url))
        
        # Check for POST without HTTPS redirect
        findings.extend(_check_post_over_http(forms, url))
        
        # Check for referer header enforcement
        findings.extend(_check_referer_checks(resp.text, url))
        
    except requests.RequestException:
        pass
    
    return findings

def _check_csrf_tokens(forms, url):
    """Check if forms contain CSRF tokens"""
    findings = []
    
    for form in forms:
        form_name = form.get('name', form.get('id', 'Unnamed Form'))
        form_action = form.get('action', '')
        form_method = form.get('method', 'GET').upper()
        
        # Skip GET forms (typically safer)
        if form_method == 'GET':
            continue
        
        # Look for hidden CSRF token fields
        token_fields = [
            'csrf_token', 'csrftoken', '_csrf', '_token', 'authenticity_token',
            'csrf', 'token', '__requestverificationtoken', '_RequestVerificationToken'
        ]
        
        hidden_inputs = form.find_all('input', {'type': 'hidden'})
        found_token = False
        token_value = None
        
        for hidden_input in hidden_inputs:
            input_name = hidden_input.get('name', '').lower()
            input_value = hidden_input.get('value', '')
            
            if any(token_field in input_name for token_field in token_fields):
                found_token = True
                token_value = input_value
                break
        
        if not found_token:
            findings.append((
                form_name,
                "Missing CSRF Token",
                "HIGH",
                f"Form '{form_name}' ({form_method} {form_action}) missing CSRF token"
            ))
        else:
            # Check if token looks weak/predictable
            if _is_weak_token(token_value):
                findings.append((
                    form_name,
                    "Weak CSRF Token",
                    "MEDIUM",
                    f"Form '{form_name}' has weak/predictable token: {token_value[:20]}..."
                ))
    
    return findings

def _check_samesite_cookies(headers, url):
    """Check for SameSite cookie attribute"""
    findings = []
    
    set_cookie = headers.get('Set-Cookie', '')
    if not set_cookie:
        return findings
    
    # Parse multiple Set-Cookie headers
    cookies = set_cookie.split(',') if isinstance(set_cookie, str) else [set_cookie]
    
    for cookie in cookies:
        cookie = cookie.strip()
        if not cookie:
            continue
        
        # Check if SameSite attribute is present
        if 'SameSite' not in cookie and 'samesite' not in cookie.lower():
            # Extract cookie name
            cookie_name = cookie.split('=')[0].strip()
            findings.append((
                cookie_name,
                "Missing SameSite Cookie Attribute",
                "MEDIUM",
                f"Cookie '{cookie_name}' missing SameSite attribute, vulnerable to CSRF"
            ))
        elif 'SameSite=None' in cookie or 'samesite=none' in cookie.lower():
            cookie_name = cookie.split('=')[0].strip()
            findings.append((
                cookie_name,
                "SameSite=None Cookie",
                "MEDIUM",
                f"Cookie '{cookie_name}' has SameSite=None, requires Secure flag"
            ))
    
    return findings

def _check_post_over_http(forms, url):
    """Check if POST forms use HTTP instead of HTTPS"""
    findings = []
    
    parts = urlsplit(url)
    
    for form in forms:
        form_name = form.get('name', form.get('id', 'Unnamed Form'))
        form_action = form.get('action', '')
        form_method = form.get('method', 'GET').upper()
        
        if form_method != 'POST':
            continue
        
        # Resolve form action to full URL
        if form_action:
            if form_action.startswith('http'):
                form_url = form_action
            else:
                form_url = urljoin(url, form_action)
        else:
            form_url = url
        
        # Check if form submits over HTTP
        if form_url.startswith('http://'):
            findings.append((
                form_name,
                "POST Over HTTP",
                "HIGH",
                f"Form '{form_name}' submits to HTTP URL: {form_url}"
            ))
    
    return findings

def _check_referer_checks(html_content, url):
    """Check if page implements referer header checks"""
    findings = []
    
    # Look for common patterns that validate referer headers
    referer_patterns = [
        r'document\.referrer',
        r'REFERER|Referer',
        r'_referer|referer_check',
        r'checkReferer|validateReferer'
    ]
    
    referer_found = False
    for pattern in referer_patterns:
        if re.search(pattern, html_content, re.IGNORECASE):
            referer_found = True
            break
    
    if not referer_found:
        findings.append((
            "Global",
            "No Referer Validation",
            "MEDIUM",
            "Page does not appear to validate HTTP Referer header"
        ))
    
    return findings

def _is_weak_token(token):
    """Check if CSRF token appears weak/predictable"""
    if not token:
        return True
    
    # Check for sequential/predictable patterns
    if re.match(r'^\d+$', token):
        return True  # All numbers
    
    if len(token) < 16:
        return True  # Too short
    
    # Check if token is very simple
    if re.match(r'^[a-f0-9]+$', token) and len(set(token)) < 8:
        return True  # Limited character set
    
    return False
