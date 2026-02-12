"""
Report generation for vulnerability scan results.
Supports multiple formats: PDF, HTML, JSON, CSV
Includes PoC, executive summary, and visualizations.
"""

import json
import csv
import os
from datetime import datetime
from collections import defaultdict
import base64

class ReportGenerator:
    """Generate scan reports in multiple formats."""
    
    def __init__(self, scan_results, config, output_dir='pdfs'):
        self.results = scan_results
        self.config = config
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.timestamp = datetime.now()
        self.scan_id = self.timestamp.strftime('%Y%m%d_%H%M%S')
    
    def generate_json(self):
        """Generate JSON report."""
        report_data = {
            'scan_id': self.scan_id,
            'timestamp': self.timestamp.isoformat(),
            'target_url': self.config.url,
            'profile': self.config.profile_name,
            'scan_config': {
                'max_urls': self.config.max_urls,
                'timeout': self.config.timeout,
                'depth_limit': self.config.depth_limit,
                'modules': self.config.modules,
                'retries': self.config.retries,
            },
            'vulnerabilities': self.results.get('vulnerabilities', {}),
            'sitemap_urls': self.results.get('sitemap_urls', []),
            'summary': self._generate_summary(),
            'executive_summary': self._generate_executive_summary(),
            'proof_of_concepts': self._generate_poc_data()
        }
        
        filename = f"report_{self.scan_id}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return filepath, report_data
    
    def generate_csv(self):
        """Generate CSV report."""
        filename = f"report_{self.scan_id}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        vulnerabilities = self.results.get('vulnerabilities', {})
        all_findings = []
        
        # SQLi findings
        for vuln in vulnerabilities.get('sqli', []):
            all_findings.append({
                'Type': 'SQL Injection',
                'Severity': 'High',
                'URL': vuln.get('url'),
                'Parameter': vuln.get('parameter'),
                'Payload': vuln.get('payload'),
                'Detection Type': vuln.get('type')
            })
        
        # XSS findings
        for vuln in vulnerabilities.get('xss', []):
            all_findings.append({
                'Type': 'Cross-Site Scripting',
                'Severity': 'High',
                'URL': vuln.get('url'),
                'Parameter': vuln.get('parameter'),
                'Payload': vuln.get('payload'),
                'Detection Type': vuln.get('type')
            })
        
        # CSRF findings
        for vuln in vulnerabilities.get('csrf', []):
            all_findings.append({
                'Type': 'CSRF',
                'Severity': 'Medium',
                'URL': vuln.get('url'),
                'Parameter': 'Form/Component',
                'Payload': str(vuln.get('finding')),
                'Detection Type': 'CSRF Detection'
            })
        
        if all_findings:
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=all_findings[0].keys())
                writer.writeheader()
                writer.writerows(all_findings)
        
        return filepath
    
    def generate_html(self):
        """Generate HTML report."""
        vulnerabilities = self.results.get('vulnerabilities', {})
        summary = self._generate_summary()
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Web Security Scan Report</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
                .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
                .header p {{ font-size: 1.1em; opacity: 0.9; }}
                .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }}
                .summary-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .summary-card h3 {{ color: #667eea; margin-bottom: 10px; font-size: 0.9em; text-transform: uppercase; }}
                .summary-card .number {{ font-size: 2.5em; font-weight: bold; }}
                .summary-card.critical {{ border-left: 4px solid #e74c3c; }}
                .summary-card.high {{ border-left: 4px solid #f39c12; }}
                .summary-card.medium {{ border-left: 4px solid #f1c40f; }}
                .summary-card.low {{ border-left: 4px solid #2ecc71; }}
                .section {{ background: white; padding: 25px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .section h2 {{ color: #667eea; margin-bottom: 20px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }}
                .section h3 {{ color: #764ba2; margin-top: 15px; margin-bottom: 10px; }}
                .vulnerability {{ background: #f9f9f9; padding: 15px; margin-bottom: 15px; border-left: 3px solid #e74c3c; border-radius: 4px; }}
                .vulnerability.high {{ border-left-color: #e74c3c; }}
                .vulnerability.medium {{ border-left-color: #f39c12; }}
                .vulnerability.low {{ border-left-color: #2ecc71; }}
                .vulnerability-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
                .vulnerability-type {{ font-weight: bold; color: #333; }}
                .severity {{ padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; }}
                .severity.critical {{ background: #e74c3c; color: white; }}
                .severity.high {{ background: #e74c3c; color: white; }}
                .severity.medium {{ background: #f39c12; color: white; }}
                .severity.low {{ background: #2ecc71; color: white; }}
                .poc {{ background: #f5f5f5; padding: 10px; border-radius: 4px; margin: 5px 0; font-family: monospace; font-size: 0.9em; overflow-x: auto; }}
                .poc-label {{ font-weight: bold; color: #667eea; margin-bottom: 5px; }}
                .footer {{ text-align: center; color: #999; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th {{ background: #f5f5f5; padding: 10px; text-align: left; border-bottom: 2px solid #ddd; }}
                td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                tr:hover {{ background: #f9f9f9; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔒 Web Security Scan Report</h1>
                    <p>Target: {self.config.url}</p>
                    <p>Scan Date: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="summary-grid">
                    <div class="summary-card critical">
                        <h3>Critical Issues</h3>
                        <div class="number">{len(vulnerabilities.get('sqli', []))}</div>
                        <p>SQL Injection</p>
                    </div>
                    <div class="summary-card high">
                        <h3>High Issues</h3>
                        <div class="number">{len(vulnerabilities.get('xss', []))}</div>
                        <p>XSS Vulnerabilities</p>
                    </div>
                    <div class="summary-card medium">
                        <h3>Medium Issues</h3>
                        <div class="number">{len(vulnerabilities.get('csrf', []))}</div>
                        <p>CSRF Weaknesses</p>
                    </div>
                    <div class="summary-card">
                        <h3>URLs Scanned</h3>
                        <div class="number">{len(self.results.get('sitemap_urls', []))}</div>
                        <p>Total endpoints</p>
                    </div>
                </div>
                
                {self._generate_html_vulnerabilities_section(vulnerabilities)}
                
                <div class="section">
                    <h2>📊 Executive Summary</h2>
                    {self._generate_html_executive_summary()}
                </div>
                
                <div class="footer">
                    <p>Generated by Web Security Scanner v1.0.0</p>
                    <p>Report ID: {self.scan_id}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        filename = f"report_{self.scan_id}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(html_content)
        
        return filepath
    
    def _generate_html_vulnerabilities_section(self, vulnerabilities):
        """Generate HTML vulnerabilities section."""
        html = '<div class="section"><h2>🔍 Vulnerabilities Found</h2>'
        
        # SQLi
        if vulnerabilities.get('sqli'):
            html += '<h3>SQL Injection (Critical)</h3>'
            for vuln in vulnerabilities['sqli']:
                html += f"""
                <div class="vulnerability high">
                    <div class="vulnerability-header">
                        <span class="vulnerability-type">Parameter: {vuln.get('parameter')}</span>
                        <span class="severity high">CRITICAL</span>
                    </div>
                    <p><strong>URL:</strong> {vuln.get('url')}</p>
                    <p><strong>Type:</strong> {vuln.get('type')}</p>
                    <div class="poc-label">Payload:</div>
                    <div class="poc">{vuln.get('payload')}</div>
                </div>
                """
        
        # XSS
        if vulnerabilities.get('xss'):
            html += '<h3>Cross-Site Scripting (High)</h3>'
            for vuln in vulnerabilities['xss']:
                html += f"""
                <div class="vulnerability high">
                    <div class="vulnerability-header">
                        <span class="vulnerability-type">Parameter: {vuln.get('parameter')}</span>
                        <span class="severity high">HIGH</span>
                    </div>
                    <p><strong>URL:</strong> {vuln.get('url')}</p>
                    <p><strong>Type:</strong> {vuln.get('type')}</p>
                    <div class="poc-label">Payload:</div>
                    <div class="poc">{vuln.get('payload')}</div>
                </div>
                """
        
        # CSRF
        if vulnerabilities.get('csrf'):
            html += '<h3>CSRF (Medium)</h3>'
            for vuln in vulnerabilities['csrf']:
                html += f"""
                <div class="vulnerability medium">
                    <div class="vulnerability-header">
                        <span class="vulnerability-type">CSRF Weakness</span>
                        <span class="severity medium">MEDIUM</span>
                    </div>
                    <p><strong>URL:</strong> {vuln.get('url')}</p>
                    <div class="poc-label">Details:</div>
                    <div class="poc">{str(vuln.get('finding'))}</div>
                </div>
                """
        
        if not any([vulnerabilities.get('sqli'), vulnerabilities.get('xss'), vulnerabilities.get('csrf')]):
            html += '<p style="color: #2ecc71; font-weight: bold;">✓ No vulnerabilities found!</p>'
        
        html += '</div>'
        return html
    
    def _generate_html_executive_summary(self):
        """Generate HTML executive summary."""
        summary = self._generate_summary()
        vulns = self.results.get('vulnerabilities', {})
        
        risk_level = 'Low'
        if summary['critical_count'] > 0:
            risk_level = 'Critical'
        elif summary['high_count'] > 0:
            risk_level = 'High'
        elif summary['medium_count'] > 0:
            risk_level = 'Medium'
        
        return f"""
        <p><strong>Risk Level:</strong> <span style="color: {'#e74c3c' if risk_level in ['Critical', 'High'] else '#f39c12' if risk_level == 'Medium' else '#2ecc71'}; font-weight: bold;">{risk_level}</span></p>
        <p><strong>Total Vulnerabilities Found:</strong> {summary['total_count']}</p>
        <ul>
            <li>Critical (SQLi): {summary['critical_count']}</li>
            <li>High (XSS): {summary['high_count']}</li>
            <li>Medium (CSRF): {summary['medium_count']}</li>
        </ul>
        <p><strong>Scan Coverage:</strong> {len(self.results.get('sitemap_urls', []))} URLs scanned out of {self.config.max_urls} configured</p>
        <p><strong>Recommendations:</strong></p>
        <ul>
            <li>Patch all SQL injection vulnerabilities immediately</li>
            <li>Implement input validation and parameterized queries</li>
            <li>Add CSRF tokens to forms</li>
            <li>Use security headers (CSP, X-Frame-Options, etc.)</li>
            <li>Conduct a comprehensive security audit</li>
        </ul>
        """
    
    def _generate_summary(self):
        """Generate vulnerability summary."""
        vulns = self.results.get('vulnerabilities', {})
        return {
            'critical_count': len(vulns.get('sqli', [])),
            'high_count': len(vulns.get('xss', [])),
            'medium_count': len(vulns.get('csrf', [])),
            'total_count': sum(len(v) for v in vulns.values())
        }
    
    def _generate_executive_summary(self):
        """Generate executive summary text."""
        summary = self._generate_summary()
        vulns = self.results.get('vulnerabilities', {})
        
        text = f"""
        Executive Summary:
        - Target: {self.config.url}
        - Scan Date: {self.timestamp.isoformat()}
        - Vulnerabilities Found: {summary['total_count']}
          * SQL Injection: {summary['critical_count']}
          * Cross-Site Scripting: {summary['high_count']}
          * CSRF: {summary['medium_count']}
        - URLs Scanned: {len(self.results.get('sitemap_urls', []))}
        """
        return text
    
    def _generate_poc_data(self):
        """Generate proof of concept data."""
        poc_data = {
            'sqli': [],
            'xss': [],
            'csrf': []
        }
        
        vulns = self.results.get('vulnerabilities', {})
        
        for vuln in vulns.get('sqli', []):
            poc_data['sqli'].append({
                'url': vuln.get('url'),
                'parameter': vuln.get('parameter'),
                'payload': vuln.get('payload'),
                'type': vuln.get('type'),
                'request': f"GET {vuln.get('url')}?{vuln.get('parameter')}={vuln.get('payload')} HTTP/1.1"
            })
        
        for vuln in vulns.get('xss', []):
            poc_data['xss'].append({
                'url': vuln.get('url'),
                'parameter': vuln.get('parameter'),
                'payload': vuln.get('payload'),
                'type': vuln.get('type'),
                'request': f"GET {vuln.get('url')}?{vuln.get('parameter')}={vuln.get('payload')} HTTP/1.1"
            })
        
        return poc_data
