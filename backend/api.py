"""
Flask REST API server for the SQL Injection, XSS, and CSRF vulnerability scanner.
Provides endpoints for scanning URLs and retrieving scan results with advanced features.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import time
from datetime import datetime
import threading
import uuid
import base64
import glob
import requests
from urllib.parse import urlparse
from crawler import crawl_site
from detector import test_sqli
from xss_detector import test_xss
from csrf_detector import test_csrf
from config import ScanConfig, SCAN_PROFILES, setup_logger
from report_generator import ReportGenerator
from scan_history import ScanHistoryTracker

app = Flask(__name__)
CORS(app, 
    resources={r"/*": {"origins": [
         "http://localhost:3000",
         "http://127.0.0.1:3000",
         "http://localhost:3001",
         "http://127.0.0.1:3001",
         "http://localhost:5173",
         "http://127.0.0.1:5173"
    ]}},
    methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"])

# Configure upload/download folders
SITEMAP_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'sitemap')
PDF_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'pdfs')
HISTORY_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'scan_history')

# Create folders if they don't exist
os.makedirs(SITEMAP_FOLDER, exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(HISTORY_FOLDER, exist_ok=True)

# Initialize tracker
history_tracker = ScanHistoryTracker()

# Async scan state
progress_store = {}
cancel_flags = set()
progress_lock = threading.Lock()


class ScanCancelled(Exception):
    """Raised when a scan is cancelled."""
    pass


def _set_progress(scan_id, **updates):
    with progress_lock:
        if scan_id not in progress_store:
            progress_store[scan_id] = {}
        progress_store[scan_id].update(updates)


def _get_progress(scan_id):
    with progress_lock:
        return progress_store.get(scan_id, {}).copy()


def _build_config(data):
    url = data.get('url', '').strip()
    profile = data.get('profile', 'standard')
    custom_config = data.get('custom_config', {}) or {}
    
    # Support camelCase config keys from frontend
    if 'maxUrls' in custom_config and 'max_urls' not in custom_config:
        custom_config['max_urls'] = custom_config.get('maxUrls')
    if 'depthLimit' in custom_config and 'depth_limit' not in custom_config:
        custom_config['depth_limit'] = custom_config.get('depthLimit')
    if 'customPayloads' in custom_config and 'custom_payloads' not in custom_config:
        custom_config['custom_payloads'] = custom_config.get('customPayloads')
    
    # Support legacy boolean flags for module selection
    legacy_sqli = data.get('check_sqli', data.get('checkSQLi'))
    legacy_xss = data.get('check_xss', data.get('checkXSS'))
    legacy_csrf = data.get('check_csrf', data.get('checkCSRF'))
    
    if 'modules' not in custom_config and any(v is not None for v in [legacy_sqli, legacy_xss, legacy_csrf]):
        modules = []
        if legacy_sqli is True:
            modules.append('sqli')
        if legacy_xss is True:
            modules.append('xss')
        if legacy_csrf is True:
            modules.append('csrf')
        custom_config['modules'] = modules
    
    if 'modules' in data and 'modules' not in custom_config:
        custom_config['modules'] = data.get('modules')
    
    return url, profile, custom_config


def _detect_server_type(target_url):
    """Detect server type using HTTP response headers."""
    try:
        response = requests.head(target_url, timeout=8, allow_redirects=True)
        server_header = response.headers.get('Server', '').strip()
        if not server_header:
            response = requests.get(target_url, timeout=8, allow_redirects=True)
            server_header = response.headers.get('Server', '').strip()

        server_lower = server_header.lower()
        if 'apache' in server_lower:
            server_type = 'Apache'
        elif 'nginx' in server_lower:
            server_type = 'Nginx'
        elif 'iis' in server_lower or 'microsoft-iis' in server_lower:
            server_type = 'IIS'
        else:
            server_type = server_header.split('/')[0] if server_header else 'Unknown'

        return {
            'type': server_type or 'Unknown',
            'header': server_header or 'Unknown',
            'detected': server_header != ''
        }
    except Exception:
        return {
            'type': 'Unknown',
            'header': 'Unknown',
            'detected': False
        }


def _perform_scan(config, url, scan_id=None):
    scan_started_at = datetime.now()
    scan_start_perf = time.perf_counter()
    results = {
        'sqli': [],
        'xss': [],
        'csrf': []
    }
    sitemap_urls = []
    errors_encountered = 0
    request_count = 0
    response_count = 0
    detector_timings_ms = []
    total_forms_detected = 0
    tested_parameters = set()
    payload_entries = []
    server_info = _detect_server_type(url)
    request_count += 1
    if server_info.get('detected'):
        response_count += 1
    
    if scan_id:
        _set_progress(scan_id, status='scanning', currentUrl=0, totalUrls=0,
                      message='Crawling site...', findings={'sqli': 0, 'xss': 0, 'csrf': 0})
    
    # Crawl site with configured depth
    config.logger.info(f"Crawling site (max_urls: {config.max_urls})...")
    sitemap_urls = crawl_site(
        url,
        max_urls=config.max_urls,
        timeout=config.timeout,
        depth_limit=config.depth_limit
    )
    config.logger.info(f"Found {len(sitemap_urls)} URLs")
    
    if scan_id:
        _set_progress(scan_id, totalUrls=len(sitemap_urls))
    
    # Scan each URL
    for idx, scan_url in enumerate(sitemap_urls, start=1):
        if scan_id and scan_id in cancel_flags:
            raise ScanCancelled()
        
        config.logger.debug(f"Scanning URL {idx}/{len(sitemap_urls)}: {scan_url}")
        if scan_id:
            _set_progress(scan_id, currentUrl=idx, message=f"Scanning {scan_url}")
        
        # SQL Injection scan
        if config.is_module_enabled('sqli'):
            for attempt in range(config.retries):
                try:
                    sqli_start = time.perf_counter()
                    request_count += 1
                    sqli_findings = test_sqli(scan_url, custom_payloads=config.payload_set.get('sqli'))
                    detector_timings_ms.append((time.perf_counter() - sqli_start) * 1000)
                    response_count += 1
                    if sqli_findings:
                        for param, payload, sqli_type in sqli_findings:
                            tested_parameters.add(param)
                            results['sqli'].append({
                                'url': scan_url,
                                'parameter': param,
                                'param': param,
                                'payload': payload,
                                'type': sqli_type
                            })
                            payload_entries.append({
                                'vulnerabilityType': 'SQL Injection',
                                'payloadUsed': payload,
                                'status': 'Successful',
                                'responseCode': 'N/A'
                            })
                        config.logger.warning(f"SQLi found in {scan_url}: {len(sqli_findings)} issues")
                    break
                except Exception as e:
                    errors_encountered += 1
                    config.logger.debug(f"SQLi scan attempt {attempt+1} failed: {str(e)}")
                    if attempt == config.retries - 1:
                        raise
        
        # XSS scan
        if config.is_module_enabled('xss'):
            for attempt in range(config.retries):
                try:
                    xss_start = time.perf_counter()
                    request_count += 1
                    xss_findings = test_xss(scan_url, custom_payloads=config.payload_set.get('xss'))
                    detector_timings_ms.append((time.perf_counter() - xss_start) * 1000)
                    response_count += 1
                    if xss_findings:
                        for param, payload, xss_type in xss_findings:
                            tested_parameters.add(param)
                            results['xss'].append({
                                'url': scan_url,
                                'parameter': param,
                                'param': param,
                                'payload': payload,
                                'type': xss_type
                            })
                            payload_entries.append({
                                'vulnerabilityType': 'Cross-Site Scripting',
                                'payloadUsed': payload,
                                'status': 'Successful',
                                'responseCode': 'N/A'
                            })
                        config.logger.warning(f"XSS found in {scan_url}: {len(xss_findings)} issues")
                    break
                except Exception as e:
                    errors_encountered += 1
                    config.logger.debug(f"XSS scan attempt {attempt+1} failed: {str(e)}")
                    if attempt == config.retries - 1:
                        raise
        
        # CSRF scan
        if config.is_module_enabled('csrf'):
            for attempt in range(config.retries):
                try:
                    csrf_start = time.perf_counter()
                    request_count += 1
                    csrf_findings = test_csrf(scan_url, sitemap_urls)
                    detector_timings_ms.append((time.perf_counter() - csrf_start) * 1000)
                    response_count += 1
                    if csrf_findings:
                        for finding in csrf_findings:
                            if isinstance(finding, (list, tuple)) and len(finding) >= 4:
                                form_name, vuln_type, severity, details = finding[:4]
                            elif isinstance(finding, dict):
                                form_name = finding.get('formName') or finding.get('form') or 'Unknown'
                                vuln_type = finding.get('vulnerability_type') or finding.get('type') or 'CSRF Detection'
                                severity = finding.get('severity') or 'MEDIUM'
                                details = finding.get('details') or finding.get('message') or ''
                            else:
                                form_name = 'Unknown'
                                vuln_type = 'CSRF Detection'
                                severity = 'MEDIUM'
                                details = str(finding)
                            
                            results['csrf'].append({
                                'url': scan_url,
                                'formName': form_name,
                                'vulnerability_type': vuln_type,
                                'type': vuln_type,
                                'severity': severity,
                                'details': details
                            })
                            total_forms_detected += 1
                            payload_entries.append({
                                'vulnerabilityType': 'CSRF',
                                'payloadUsed': 'Form security test',
                                'status': 'Detected',
                                'responseCode': 'N/A'
                            })
                        config.logger.warning(f"CSRF found in {scan_url}: {len(csrf_findings)} issues")
                    break
                except Exception as e:
                    errors_encountered += 1
                    config.logger.debug(f"CSRF scan attempt {attempt+1} failed: {str(e)}")
                    if attempt == config.retries - 1:
                        raise
        
        if scan_id:
            _set_progress(scan_id, findings={
                'sqli': len(results['sqli']),
                'xss': len(results['xss']),
                'csrf': len(results['csrf'])
            })
    
    config.logger.info("Scan completed")
    scan_ended_at = datetime.now()
    scan_duration_seconds = max(0.0, time.perf_counter() - scan_start_perf)
    average_response_time_ms = (
        sum(detector_timings_ms) / len(detector_timings_ms) if detector_timings_ms else 0.0
    )
    
    # Prepare response
    response_data = {
        'success': True,
        'url': url,
        'profile': config.profile_name,
        'timestamp': datetime.now().isoformat(),
        'scan_start_time': scan_started_at.isoformat(),
        'scan_end_time': scan_ended_at.isoformat(),
        'scan_duration_seconds': round(scan_duration_seconds, 2),
        'server': server_info,
        'performance': {
            'total_requests_sent': request_count,
            'total_responses_received': response_count,
            'average_response_time_ms': round(average_response_time_ms, 2),
            'scan_mode': 'Async' if scan_id else 'Sync',
            'thread_count_used': 1,
            'errors_encountered': errors_encountered,
            'total_forms_detected': total_forms_detected,
            'total_input_parameters_tested': len(tested_parameters),
            'payload_metrics': {
                'total_payloads_tested': len(payload_entries),
                'successful_payloads': len([p for p in payload_entries if p.get('status') != 'Blocked']),
                'blocked_payloads': len([p for p in payload_entries if p.get('status') == 'Blocked']),
                'entries': payload_entries
            }
        },
        'vulnerabilities': results,
        'sitemap_urls': sitemap_urls,
        'sitemapData': {
            'urls': sitemap_urls,
            'totalUrls': len(sitemap_urls),
            'sitemapImage': _load_latest_sitemap_image(url)
        },
        'summary': {
            'sqli_found': len(results['sqli']) > 0,
            'xss_found': len(results['xss']) > 0,
            'csrf_found': len(results['csrf']) > 0,
            'total_vulnerabilities': sum(len(v) for v in results.values()),
            'sqli_count': len(results['sqli']),
            'xss_count': len(results['xss']),
            'csrf_count': len(results['csrf'])
        }
    }
    
    return response_data


def _load_latest_sitemap_image(target_url):
    """Load latest sitemap image for a URL as data URL."""
    try:
        domain = urlparse(target_url).netloc.replace(".", "_")
        pattern = os.path.join(SITEMAP_FOLDER, f"sitemap_{domain}_*.png")
        matches = glob.glob(pattern)
        if not matches:
            return None
        latest = max(matches, key=os.path.getmtime)
        with open(latest, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
        return f"data:image/png;base64,{encoded}"
    except Exception:
        return None


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'message': 'API is running'}), 200


@app.route('/info', methods=['GET'])
def info():
    """Return API information."""
    return jsonify({
        'name': 'Web Security Scanner API',
        'version': '2.0.0',
        'features': [
            'SQL Injection Detection',
            'XSS Detection',
            'CSRF Detection',
            'Custom Payloads',
            'Multiple Report Formats',
            'Scan History & Regression Tracking',
            'Real-time Progress Tracking',
            'Configurable Scan Profiles'
        ],
        'endpoints': {
            '/health': 'GET - Health check',
            '/info': 'GET - API information',
            '/profiles': 'GET - Available scan profiles',
            '/scan': 'POST - Scan URL for vulnerabilities',
            '/scan/async': 'POST - Async scan with real-time updates',
            '/scan/status': 'GET - Get async scan status',
            '/scan/stop': 'POST - Stop async scan',
            '/sitemap': 'GET - Get sitemap for URL',
            '/report': 'POST - Generate report in multiple formats',
            '/history': 'GET - Get scan history for URL',
            '/compare': 'GET - Compare two scans for regressions'
        }
    }), 200


@app.route('/profiles', methods=['GET', 'OPTIONS'])
def get_profiles():
    """Get available scan profiles."""
    if request.method == 'OPTIONS':
        return '', 204
    
    profiles = {}
    for name, profile in SCAN_PROFILES.items():
        profiles[name] = {
            'name': profile.get('name'),
            'description': profile.get('description'),
            'max_urls': profile.get('max_urls'),
            'depth_limit': profile.get('depth_limit'),
            'timeout': profile.get('timeout'),
            'modules': profile.get('modules'),
            'payloads': profile.get('payloads')
        }
    
    return jsonify({'profiles': profiles}), 200


@app.route('/scan', methods=['POST', 'OPTIONS'])
def scan():
    """
    Scan a URL for vulnerabilities.
    
    Expected JSON payload:
    {
        "url": "http://example.com",
        "profile": "standard",  # quick, standard, full, aggressive
        "custom_config": {
            "max_urls": 50,
            "depth_limit": 2,
            "timeout": 10,
            "verbose": true,
            "modules": ["sqli", "xss", "csrf"],
            "custom_payloads": {
                "sqli": ["' OR '1'='1"],
                "xss": ["<script>alert(1)</script>"]
            }
        }
    }
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json() or {}
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        url, profile, custom_config = _build_config(data)
        
        # Validate URL
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        # Create scan config
        config = ScanConfig(url, profile, custom_config)
        config.logger.info(f"Starting scan: {url} with profile: {profile}")
        
        response_data = _perform_scan(config, url)
        
        # Save to history
        history_tracker.save_scan(url, response_data, config)
        
        return jsonify(response_data), 200
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'message': 'An error occurred during scanning'
        }), 500


@app.route('/scan/async', methods=['POST', 'OPTIONS'])
def scan_async():
    """Start an async scan and return a scan_id for progress polling."""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json() or {}
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        url, profile, custom_config = _build_config(data)
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        scan_id = str(uuid.uuid4())
        _set_progress(scan_id, status='queued', currentUrl=0, totalUrls=0,
                      message='Scan queued', findings={'sqli': 0, 'xss': 0, 'csrf': 0})
        
        def run_scan():
            try:
                config = ScanConfig(url, profile, custom_config)
                config.logger.info(f"Starting async scan: {url} with profile: {profile}")
                _set_progress(scan_id, status='scanning', message='Starting scan...')
                
                response_data = _perform_scan(config, url, scan_id=scan_id)
                history_tracker.save_scan(url, response_data, config)
                
                _set_progress(scan_id, status='completed', result=response_data, message='Scan completed')
            except ScanCancelled:
                _set_progress(scan_id, status='canceled', message='Scan canceled by user')
            except Exception as e:
                _set_progress(scan_id, status='error', message=str(e))
        
        thread = threading.Thread(target=run_scan, daemon=True)
        thread.start()
        
        return jsonify({'success': True, 'scan_id': scan_id}), 202
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while starting async scan'
        }), 500


@app.route('/scan/status', methods=['GET', 'OPTIONS'])
def scan_status():
    """Get scan progress/status by scan_id."""
    if request.method == 'OPTIONS':
        return '', 204
    
    scan_id = request.args.get('scan_id', '').strip()
    if not scan_id:
        return jsonify({'error': 'scan_id is required'}), 400
    
    progress = _get_progress(scan_id)
    if not progress:
        return jsonify({'error': 'Scan not found'}), 404
    
    return jsonify({'success': True, 'scan_id': scan_id, **progress}), 200


@app.route('/scan/stop', methods=['POST', 'OPTIONS'])
def scan_stop():
    """Stop a running scan by scan_id."""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.get_json() or {}
    scan_id = data.get('scan_id', '').strip()
    
    if not scan_id:
        return jsonify({'error': 'scan_id is required'}), 400
    
    cancel_flags.add(scan_id)
    _set_progress(scan_id, status='canceled', message='Scan cancel requested')
    return jsonify({'success': True, 'scan_id': scan_id, 'status': 'canceled'}), 200


@app.route('/sitemap', methods=['GET', 'OPTIONS'])
def get_sitemap():
    """Get sitemap for a URL."""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        url = request.args.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL parameter is required'}), 400
        
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        urls = crawl_site(url)
        
        return jsonify({
            'success': True,
            'url': url,
            'urls': urls,
            'total': len(urls)
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while crawling'
        }), 500


@app.route('/report', methods=['POST', 'OPTIONS'])
def generate_report():
    """
    Generate report in multiple formats.
    
    Expected JSON payload:
    {
        "url": "http://example.com",
        "format": "html",  # json, csv, html
        "vulnerabilities": {...},
        "sitemap_urls": [...]
    }
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        url = data.get('url', '')
        report_format = data.get('format', 'json').lower()
        profile = data.get('profile', 'standard')
        custom_config = data.get('custom_config', {})
        
        # Create minimal config for report
        config = ScanConfig(url, profile, custom_config)
        
        # Create report generator
        generator = ReportGenerator(data, config)
        
        if report_format == 'json':
            filepath, report_data = generator.generate_json()
            return jsonify({
                'success': True,
                'format': 'json',
                'filename': os.path.basename(filepath),
                'report': report_data
            }), 200
        
        elif report_format == 'csv':
            filepath = generator.generate_csv()
            return jsonify({
                'success': True,
                'format': 'csv',
                'filename': os.path.basename(filepath),
                'message': 'CSV report generated'
            }), 200
        
        elif report_format == 'html':
            filepath = generator.generate_html()
            return jsonify({
                'success': True,
                'format': 'html',
                'filename': os.path.basename(filepath),
                'message': 'HTML report generated'
            }), 200
        
        else:
            return jsonify({'error': f'Unsupported format: {report_format}'}), 400
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while generating report'
        }), 500


@app.route('/history', methods=['GET', 'OPTIONS'])
def get_history():
    """Get scan history for a URL."""
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        url = request.args.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL parameter is required'}), 400
        
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        history = history_tracker.get_scan_history(url)
        latest = history_tracker.get_latest_scan(url)
        
        return jsonify({
            'success': True,
            'url': url,
            'history': history,
            'latest': latest,
            'total_scans': len(history)
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while retrieving history'
        }), 500


@app.route('/compare', methods=['GET', 'OPTIONS'])
def compare_scans():
    """
    Compare two scans for regression detection.
    
    Query parameters:
    - url: Target URL
    - scan1: Index of first scan (optional, defaults to second-to-last)
    - scan2: Index of second scan (optional, defaults to last)
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        url = request.args.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL parameter is required'}), 400
        
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        scan1_idx = request.args.get('scan1', type=int)
        scan2_idx = request.args.get('scan2', type=int)
        
        comparison = history_tracker.compare_scans(url, scan1_idx, scan2_idx)
        
        if not comparison:
            return jsonify({
                'success': False,
                'message': 'Not enough scans to compare'
            }), 400
        
        return jsonify({
            'success': True,
            'url': url,
            'comparison': comparison
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while comparing scans'
        }), 500


@app.route('/download-pdf', methods=['POST', 'OPTIONS'])
def download_pdf():
    """
    Download scan report as PDF.
    
    Expected JSON payload:
    {
        "url": "http://example.com",
        "vulnerabilities": {...},
        "timestamp": "2024-01-27T10:30:00"
    }
    """
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        url = data.get('url', 'Unknown')
        vulnerabilities = data.get('vulnerabilities', {})
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Create filename
        safe_url = url.replace('http://', '').replace('https://', '').replace('/', '_')[:30]
        filename = f"scan_report_{safe_url}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(PDF_FOLDER, filename)
        
        # Save report data as JSON (can be converted to PDF on frontend)
        report_data = {
            'url': url,
            'timestamp': timestamp,
            'vulnerabilities': vulnerabilities,
            'summary': {
                'sqli': len(vulnerabilities.get('sqli', [])),
                'xss': len(vulnerabilities.get('xss', [])),
                'csrf': len(vulnerabilities.get('csrf', []))
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': 'Report prepared for download',
            'filename': filename
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'An error occurred while preparing the report'
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🔒 Web Security Scanner API v2.0.0")
    print("="*60)
    print("\n📍 Available Endpoints:")
    print("  GET  /health - Health check")
    print("  GET  /info - API information")
    print("  GET  /profiles - Available scan profiles")
    print("  POST /scan - Execute vulnerability scan")
    print("  GET  /sitemap - Get website sitemap")
    print("  POST /report - Generate reports (JSON, CSV, HTML)")
    print("  GET  /history - Get scan history")
    print("  GET  /compare - Compare scans (regression detection)")
    print("\n🔧 Scan Profiles Available:")
    print("  • quick - Fast scan (10 URLs, depth 1)")
    print("  • standard - Balanced scan (30 URLs, depth 2)")
    print("  • full - Comprehensive scan (100 URLs, depth 3)")
    print("  • aggressive - Maximum scan (200 URLs, depth 5)")
    print("\n🌐 Server running at http://localhost:5000")
    print("📱 CORS enabled for http://localhost:3000 and http://127.0.0.1:3000")
    print("\n✨ Features:")
    print("  ✓ SQL Injection Detection (Error, Boolean, Time-based)")
    print("  ✓ XSS Detection (Reflected)")
    print("  ✓ CSRF Detection")
    print("  ✓ Custom Payloads")
    print("  ✓ Configurable Depth & Retries")
    print("  ✓ Verbose Logging")
    print("  ✓ Multiple Report Formats")
    print("  ✓ Scan History & Regression Tracking")
    print("="*60)
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
