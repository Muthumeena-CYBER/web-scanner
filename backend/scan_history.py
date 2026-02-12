"""
Scan history tracking for regression detection and comparison.
"""

import json
import os
from datetime import datetime

class ScanHistoryTracker:
    """Track and manage scan history."""
    
    def __init__(self, history_dir='scan_history'):
        self.history_dir = os.path.join(os.path.dirname(__file__), '..', history_dir)
        os.makedirs(self.history_dir, exist_ok=True)
    
    def save_scan(self, url, results, config):
        """Save scan results to history."""
        # Create URL-specific history file
        safe_url = url.replace('http://', '').replace('https://', '').replace('/', '_')[:50]
        filename = f"history_{safe_url}.json"
        filepath = os.path.join(self.history_dir, filename)
        
        # Load existing history
        history = []
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    history = json.load(f)
            except:
                history = []
        
        # Add new scan
        scan_entry = {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'profile': config.profile_name,
            'vulnerabilities': results.get('vulnerabilities', {}),
            'sitemap_urls': results.get('sitemap_urls', []),
            'summary': {
                'sqli': len(results.get('vulnerabilities', {}).get('sqli', [])),
                'xss': len(results.get('vulnerabilities', {}).get('xss', [])),
                'csrf': len(results.get('vulnerabilities', {}).get('csrf', []))
            }
        }
        
        history.append(scan_entry)
        
        # Keep last 20 scans
        if len(history) > 20:
            history = history[-20:]
        
        # Save history
        with open(filepath, 'w') as f:
            json.dump(history, f, indent=2)
        
        return filepath
    
    def get_scan_history(self, url):
        """Get all scans for a URL."""
        safe_url = url.replace('http://', '').replace('https://', '').replace('/', '_')[:50]
        filename = f"history_{safe_url}.json"
        filepath = os.path.join(self.history_dir, filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        
        return []
    
    def get_latest_scan(self, url):
        """Get the latest scan for a URL."""
        history = self.get_scan_history(url)
        if history:
            return history[-1]
        return None
    
    def compare_scans(self, url, scan1_idx=None, scan2_idx=None):
        """Compare two scans for regression detection."""
        history = self.get_scan_history(url)
        
        if len(history) < 2:
            return None
        
        # Default to comparing last two scans
        if scan1_idx is None:
            scan1_idx = len(history) - 2
        if scan2_idx is None:
            scan2_idx = len(history) - 1
        
        scan1 = history[scan1_idx]
        scan2 = history[scan2_idx]
        
        return {
            'previous_scan': scan1,
            'current_scan': scan2,
            'improvements': self._calculate_improvements(scan1, scan2),
            'regressions': self._calculate_regressions(scan1, scan2)
        }
    
    def _calculate_improvements(self, old_scan, new_scan):
        """Calculate vulnerabilities that have been fixed."""
        improvements = {
            'sqli': [],
            'xss': [],
            'csrf': []
        }
        
        old_sqli = {f"{v['url']}_{v['parameter']}": v for v in old_scan['vulnerabilities'].get('sqli', [])}
        new_sqli = {f"{v['url']}_{v['parameter']}": v for v in new_scan['vulnerabilities'].get('sqli', [])}
        
        # Similar for XSS and CSRF
        for key in old_sqli:
            if key not in new_sqli:
                improvements['sqli'].append(old_sqli[key])
        
        return improvements
    
    def _calculate_regressions(self, old_scan, new_scan):
        """Calculate new vulnerabilities since last scan."""
        regressions = {
            'sqli': [],
            'xss': [],
            'csrf': []
        }
        
        old_sqli = {f"{v['url']}_{v['parameter']}": v for v in old_scan['vulnerabilities'].get('sqli', [])}
        new_sqli = {f"{v['url']}_{v['parameter']}": v for v in new_scan['vulnerabilities'].get('sqli', [])}
        
        # Similar for XSS and CSRF
        for key in new_sqli:
            if key not in old_sqli:
                regressions['sqli'].append(new_sqli[key])
        
        return regressions
