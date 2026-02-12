# Implementation Guide - Web Security Scanner v2.0

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- All dependencies from requirements files

### Installation & Run

#### Backend Setup
```bash
cd sqli_scanner
pip install -r backend/requirements.txt
pip install -r requirements-api.txt
```

#### Frontend Setup
```bash
cd sqli_scanner/frontend
npm install
```

#### Start Backend
```bash
# From sqli_scanner root
python backend/api.py
```

Server runs on: `http://localhost:5000`

#### Start Frontend
```bash
# From sqli_scanner/frontend
npm run dev
```

App runs on: `http://localhost:3000`

---

## NEW FEATURES QUICK REFERENCE

### 1. Scan Profiles
Available profiles accessible from Advanced Config panel:
- **Quick**: Fast scan, 10 URLs, depth 1
- **Standard**: Balanced, 30 URLs, depth 2 (default)
- **Full**: Comprehensive, 100 URLs, depth 3
- **Aggressive**: Maximum, 200 URLs, depth 5
- **Custom**: Full control over all parameters

### 2. Custom Configuration
Click "Advanced Configuration" to access:
- Profile selector
- Module toggles (SQLi, XSS, CSRF)
- URL limit (5-200)
- Depth limit (1-5)
- Timeout (5-30 seconds)
- Verbose logging toggle

### 3. Report Formats
After scan completes, download reports:
- **JSON**: Raw data and analysis
- **CSV**: Spreadsheet format
- **HTML**: Professional formatted report

### 4. Real-Time Progress
During scan:
- Progress bar shows percentage complete
- Live counter for each vulnerability type
- Current URL being scanned
- Status updates

### 5. Proof of Concepts
View detailed PoC for each vulnerability:
- Click to expand each finding
- See HTTP request format
- Copy payload to clipboard
- Detection method explanation
- Risk level indicator

### 6. Risk Visualization
- Overall risk assessment (CRITICAL/HIGH/MEDIUM/LOW)
- Pie chart of vulnerability distribution
- Bar chart showing vulnerability counts
- Detailed breakdown table

### 7. Scan History Comparison
After multiple scans:
- Select two scans to compare
- View fixed vulnerabilities
- See new vulnerabilities
- Get recommendations

---

## API ENDPOINTS

### Health & Info
```
GET /health
GET /info
GET /profiles
```

### Scanning
```
POST /scan
Body: {
  "url": "http://example.com",
  "profile": "standard",
  "custom_config": {
    "max_urls": 30,
    "depth_limit": 2,
    "timeout": 8,
    "verbose": true,
    "modules": ["sqli", "xss", "csrf"]
  }
}
```

### Reports
```
POST /report
Body: {
  "url": "http://example.com",
  "format": "json",  // json, csv, html
  "vulnerabilities": {...},
  "sitemap_urls": [...]
}
```

### History & Comparison
```
GET /history?url=http://example.com
GET /compare?url=http://example.com&scan1=0&scan2=1
```

---

## CONFIGURATION EXAMPLES

### Example 1: Fast Security Check
```json
{
  "url": "http://example.com",
  "profile": "quick"
}
```
Result: 10 URLs scanned in ~2-3 minutes

### Example 2: Custom Deep Scan
```json
{
  "url": "http://example.com",
  "profile": "custom",
  "custom_config": {
    "max_urls": 75,
    "depth_limit": 4,
    "timeout": 12,
    "verbose": true,
    "modules": ["sqli", "xss"]
  }
}
```

### Example 3: With Custom Payloads
```json
{
  "url": "http://example.com",
  "profile": "full",
  "custom_config": {
    "custom_payloads": {
      "sqli": [
        "' OR '1'='1",
        "'; DROP TABLE users--"
      ],
      "xss": [
        "<img src=x onerror='alert(1)'>",
        "<svg onload='alert(1)'>"
      ]
    }
  }
}
```

---

## OUTPUT FILES

### Reports
Generated in `pdfs/` directory:
- `report_YYYYMMDD_HHMMSS.json` - JSON report
- `report_YYYYMMDD_HHMMSS.csv` - CSV report
- `report_YYYYMMDD_HHMMSS.html` - HTML report

### Logs
Generated in `logs/` directory:
- `scan_YYYYMMDD_HHMMSS.log` - Verbose scan log

### History
Stored in `scan_history/` directory:
- `history_example_com.json` - All scans for example.com

---

## VULNERABILITY DETECTION

### SQL Injection Detection Methods
1. **Error-based**: Looks for SQL error messages
   - Works with 10+ database types
   - Immediate confirmation of vulnerability

2. **Boolean-based**: Compares true/false payloads
   - Detects by response size/status differences
   - Works when error messages hidden

3. **Time-based**: Measures response delays
   - Triggers database sleep commands
   - Detects by timing anomalies (>3s delay)

### XSS Detection
- **Reflected XSS**: Checks for payload reflection in HTML
- Multiple encoding detection
- Parameter-level analysis

### CSRF Detection
- Missing token detection
- Weak token analysis
- Cookie attribute validation
- Form security checks
- Referer validation

---

## PAYLOAD SETS

### Default Payloads
Minimal payload set for quick testing:
- 4 SQL injection payloads
- 4 XSS payloads

### Extended Payloads
Moderate coverage:
- 10 SQL injection payloads
- 10 XSS payloads

### Comprehensive Payloads
Maximum coverage:
- 16 SQL injection payloads
- 19 XSS payloads

---

## TROUBLESHOOTING

### Backend Not Starting
```bash
# Check if port 5000 is in use
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill process and restart
python backend/api.py
```

### Frontend Not Running
```bash
# Check Node version
node --version

# Clear node_modules and reinstall
rm -rf node_modules
npm install
npm run dev
```

### Scans Timing Out
- Increase timeout in Custom profile (max 30s)
- Reduce max_urls to 50
- Reduce depth_limit to 1-2

### Memory Issues
- Use Quick profile instead
- Reduce max_urls
- Clear browser cache
- Restart servers

---

## FILE STRUCTURE

```
sqli_scanner/
├── backend/
│   ├── api.py (updated with v2.0 features)
│   ├── config.py (NEW - configurations)
│   ├── crawler.py (updated with depth control)
│   ├── detector.py (updated with custom payloads)
│   ├── report_generator.py (NEW - multi-format reports)
│   ├── scan_history.py (NEW - history tracking)
│   ├── xss_detector.py (updated)
│   ├── csrf_detector.py
│   ├── payloads.py
│   ├── xss_payloads.py
│   ├── utils.py
│   ├── logs/ (NEW - verbose logging)
│   ├── requirements.txt
│   └── __pycache__/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AdvancedConfig.tsx (NEW)
│   │   │   ├── ProgressDashboard.tsx (NEW)
│   │   │   ├── ReportViewer.tsx (NEW)
│   │   │   ├── PoCViewer.tsx (NEW)
│   │   │   ├── RiskVisualization.tsx (NEW)
│   │   │   ├── ScanHistoryComparison.tsx (NEW)
│   │   │   ├── App.tsx (updated)
│   │   │   └── ...other components
│   │   ├── services/
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   └── ...config files
├── scan_history/ (NEW - history storage)
├── pdfs/ (NEW - report output)
├── sitemap/
├── ADVANCED_FEATURES_V2.md (NEW)
├── IMPLEMENTATION_GUIDE.md (NEW - this file)
└── ...other documentation
```

---

## PERFORMANCE TIPS

1. **Quick Scan**: Use "Quick" profile for testing
2. **Selective Modules**: Disable unused modules
3. **Depth Control**: Lower depth = faster scans
4. **Timeout**: Lower timeout for faster failures on unreachable URLs
5. **Retries**: Reduce retries for faster scans (1 vs 3)

---

## SECURITY CONSIDERATIONS

1. **Custom Payloads**: Be careful with custom payload injection
2. **Rate Limiting**: Respect target server rate limits
3. **Ethical Use**: Only scan sites you own or have permission to scan
4. **HTTPS**: Use HTTPS URLs when possible
5. **Logs**: Secure access to logs and reports

---

## EXTENDING THE SCANNER

### Adding New Detectors
1. Create detector file: `backend/new_detector.py`
2. Add to config profiles
3. Add API endpoint in `api.py`
4. Create frontend component

### Custom Payload Sets
1. Edit `config.py` PAYLOAD_SETS
2. Add new set with descriptive name
3. Reference in custom_config

### New Report Format
1. Add method to `ReportGenerator` class
2. Add /report endpoint handler
3. Create frontend download button

---

## TIPS FOR EVALUATION

### For Teachers/Judges
- **Show Report Formats**: Download JSON, CSV, HTML
- **Explain Profiles**: Demo Quick vs Full scan differences
- **Demonstrate Regression**: Run multiple scans and compare
- **Show PoC Details**: Expand vulnerabilities to show PoC
- **Explain Logging**: Check logs for detailed tracing

### For Recruiters
- **Code Quality**: Show config.py architecture
- **API Design**: Explain RESTful endpoint structure
- **Error Handling**: Demonstrate error messages
- **Real-time Updates**: Show progress bar during scan
- **Data Persistence**: Explain scan history implementation
- **Report Generation**: Show multi-format output
- **Frontend Polish**: Demonstrate UI responsiveness

---

## FURTHER ENHANCEMENT IDEAS

1. **WebSocket Support**: Real-time progress streaming
2. **Scheduled Scans**: Automatic scanning on schedule
3. **Notifications**: Email alerts on vulnerabilities
4. **API Keys**: Authentication for API
5. **Rate Limiting**: Prevent abuse
6. **Dashboard**: Statistics over time
7. **Custom Rules**: User-defined detection patterns
8. **Integrations**: Export to security platforms
9. **Mobile App**: React Native mobile version
10. **Cloud Deployment**: Docker containerization

---

## VERSION HISTORY

### v1.0.0 (Original)
- Basic SQLi, XSS, CSRF detection
- Web UI with Tailwind CSS
- Sitemap generation
- PDF report

### v2.0.0 (Current)
- Advanced configurations
- Scan profiles
- Custom payloads
- Multi-format reports
- Regression tracking
- Real-time progress
- Risk visualization
- PoC viewer
- Verbose logging
- History management

---

## SUPPORT

For issues or questions:
1. Check logs in `backend/logs/`
2. Review error messages in browser console
3. Test API endpoints with curl/Postman
4. Verify target URL accessibility
5. Check Python/Node versions

---

**Last Updated**: January 27, 2026
**Version**: 2.0.0
**Status**: Production Ready ✅
