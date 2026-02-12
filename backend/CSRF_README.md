# CSRF (Cross-Site Request Forgery) Vulnerability Scanner

## Overview
The CSRF detector identifies potential Cross-Site Request Forgery vulnerabilities in web applications by analyzing forms, cookies, and request mechanisms.

## Vulnerability Types Detected

### 1. **Missing CSRF Token** (HIGH Severity)
- **Description**: Forms (POST, PUT, DELETE) lack CSRF protection tokens
- **Risk**: Attackers can craft requests to perform unauthorized actions
- **Detection**: Scans for common token field names (csrf_token, _token, etc.)
- **Remediation**: Implement CSRF tokens in all state-changing forms

### 2. **Weak CSRF Token** (MEDIUM Severity)
- **Description**: CSRF tokens appear predictable or weak
- **Risk**: Attackers may be able to predict or brute-force tokens
- **Indicators**:
  - Tokens shorter than 16 characters
  - All-numeric tokens
  - Sequential patterns
  - Limited character sets
- **Remediation**: Use cryptographically random tokens (≥32 bytes)

### 3. **Missing SameSite Cookie Attribute** (MEDIUM Severity)
- **Description**: Session cookies lack the SameSite attribute
- **Risk**: Cookies sent in cross-site requests, enabling CSRF
- **Detection**: Checks Set-Cookie headers for SameSite flag
- **Remediation**: Add `SameSite=Strict` or `SameSite=Lax` to cookies

### 4. **SameSite=None Without Secure** (MEDIUM Severity)
- **Description**: Cookies set to SameSite=None but not using HTTPS
- **Risk**: Cross-site cookies transmitted over unencrypted connection
- **Remediation**: Require HTTPS when using SameSite=None

### 5. **POST Over HTTP** (HIGH Severity)
- **Description**: Forms submit sensitive data via HTTP (unencrypted)
- **Risk**: Data interception and CSRF attacks over unencrypted channels
- **Remediation**: Use HTTPS for all form submissions

### 6. **No Referer Validation** (MEDIUM Severity)
- **Description**: Application doesn't validate HTTP Referer header
- **Risk**: Cross-origin requests accepted without verification
- **Detection**: Looks for referer validation patterns in code
- **Remediation**: Implement server-side referer checks

## Token Field Detection

The scanner recognizes these common CSRF token field names:
- `csrf_token`
- `csrftoken`
- `_csrf`
- `_token`
- `authenticity_token`
- `csrf`
- `token`
- `__requestverificationtoken`
- `_RequestVerificationToken`

## CSRF Attack Vectors

### Image-based CSRF
```html
<img src="http://vulnerable.com/action?param=value">
```

### Form-based CSRF
```html
<form action="http://vulnerable.com/action" method="POST">
  <input type="hidden" name="param" value="malicious">
  <script>document.forms[0].submit();</script>
</form>
```

### XMLHttpRequest CSRF
```javascript
var xhr = new XMLHttpRequest();
xhr.open("POST", "http://vulnerable.com/action", true);
xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
xhr.send("param=malicious");
```

### Fetch API CSRF
```javascript
fetch("http://vulnerable.com/action", {
  method: "POST",
  credentials: "include",
  body: "param=malicious"
});
```

### JSON-based CSRF
```javascript
fetch("http://vulnerable.com/api/action", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  credentials: "include",
  body: JSON.stringify({param: "malicious"})
});
```

## CSRF Protection Mechanisms

### 1. **Synchronizer Token Pattern**
- Generate unique token per session/request
- Include token in all forms
- Validate token on server-side
- Discard invalid tokens

### 2. **SameSite Cookies**
```
Set-Cookie: sessionid=abc123; SameSite=Strict; Secure; HttpOnly
```
- **Strict**: Cookies only sent in same-site requests
- **Lax**: Cookies sent with top-level navigation
- **None**: Cookies sent in cross-site requests (requires Secure)

### 3. **Double-Submit Cookies**
- Store token in cookie and form parameter
- Verify both values match on server
- Requires Same-Origin Policy

### 4. **Custom Request Headers**
- JavaScript framework (Angular, React) adds custom header
- Server verifies header presence
- Cannot be set by simple HTML forms

### 5. **Referer Header Validation**
```
if (request.referer != request.host) {
  reject();
}
```

## Remediation Steps

### For Developers
1. **Implement Synchronizer Tokens**: Use cryptographically secure random generation
2. **Set SameSite Cookies**: Add `SameSite=Strict` for sensitive operations
3. **Use HTTPS**: Enforce HTTPS for all state-changing operations
4. **Validate Origin/Referer**: Check request origin server-side
5. **Implement CORS properly**: Define strict CORS policies

### For DevOps/Security Teams
1. **Enable HSTS**: Enforce HTTPS globally
2. **Monitor**: Track CSRF attempts in logs
3. **WAF Rules**: Implement Web Application Firewall CSRF protections
4. **Security Headers**: Add X-Frame-Options, X-Content-Type-Options

## Usage

```bash
python scanner.py http://target-website.com
```

The scanner will test all discovered URLs for CSRF vulnerabilities and report:
- Vulnerable forms
- Missing protections
- Weak token implementations
- Cookie security issues

## Output Example

```
[!] CSRF Vulnerability Found: http://target.com/user/profile
    ├─ Form/Component: edit_profile
    ├─ Vulnerability Type: Missing CSRF Token
    ├─ Severity: HIGH
    └─ Details: Form 'edit_profile' (POST /update) missing CSRF token

    ├─ Form/Component: session_cookie
    ├─ Vulnerability Type: Missing SameSite Cookie Attribute
    ├─ Severity: MEDIUM
    └─ Details: Cookie 'sessionid' missing SameSite attribute, vulnerable to CSRF
```

## References
- [OWASP CSRF](https://owasp.org/www-community/attacks/csrf)
- [CWE-352: Cross-Site Request Forgery](https://cwe.mitre.org/data/definitions/352.html)
- [SameSite Cookie Attribute](https://tools.ietf.org/html/draft-west-first-party-cookies)
- [NIST Security Guidelines](https://csrc.nist.gov/publications/detail/sp/800-63-3/final)
