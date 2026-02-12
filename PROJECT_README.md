# Web Security Scanner - Complete Project

A comprehensive web vulnerability scanning and reporting platform with a modern React frontend and Python backend.

## 🎯 Features

### Vulnerability Detection
- **SQL Injection (SQLi)**: Error-based, Boolean-based, and Time-based detection
- **Cross-Site Scripting (XSS)**: Reflected XSS detection via GET parameters
- **Cross-Site Request Forgery (CSRF)**: Token analysis, cookie validation, referer checks

### Web Interface
- 🎨 Modern, responsive UI with Tailwind CSS
- 🔒 Three toggleable vulnerability checkers (all default selected)
- 📊 Real-time scan progress and results
- 🗺️ Visual sitemap of discovered URLs
- 📄 Professional PDF report generation
- 📱 Mobile-friendly design

### Backend Capabilities
- 🕷️ Automated URL crawling and site mapping
- 🔍 Multi-threaded vulnerability scanning
- 📈 Detailed hierarchy visualization
- 💾 Sitemap storage and management
- ⚡ Optimized request handling

## 📋 Requirements

- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **npm** or **yarn**: Package manager
- **Modern Browser**: Chrome, Firefox, Safari, or Edge
- **RAM**: 2GB minimum, 4GB+ recommended
- **Storage**: 500MB for dependencies + scan results

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
cd sqli_scanner
quickstart.bat
```

**Linux/macOS:**
```bash
cd sqli_scanner
chmod +x quickstart.sh
./quickstart.sh
```

### Option 2: Manual Setup

#### Step 1: Backend Installation
```bash
cd sqli_scanner
pip install -r backend/requirements.txt
pip install -r requirements-api.txt
```

#### Step 2: Frontend Installation
```bash
cd frontend
npm install
```

#### Step 3: Start Backend API
```bash
# From sqli_scanner root directory
python api.py
```
Expected: API running on `http://localhost:5000`

#### Step 4: Start Frontend
```bash
# From sqli_scanner/frontend directory
npm run dev
```
Expected: App running on `http://localhost:3000`

#### Step 5: Access Application
Open browser to: **http://localhost:3000**

## 📖 Usage Guide

### Basic Scanning Workflow

1. **Enter Target URL**
   ```
   https://example.com
   ```

2. **Select Vulnerability Types**
   - ☑️ SQL Injection (SQLi)
   - ☑️ Cross-Site Scripting (XSS)
   - ☑️ Cross-Site Request Forgery (CSRF)
   (All selected by default)

3. **Initiate Scan**
   - Click "Start Scan" button
   - Monitor progress (1-5 minutes typical)

4. **Review Results**
   - **Sitemap**: Visual structure of discovered URLs
   - **Vulnerability Cards**: Color-coded by type
   - **Risk Level**: CRITICAL/HIGH/MEDIUM/LOW assessment
   - **Severity Badges**: Individual finding severity

5. **Generate Report**
   - Review formatted scan report
   - Click "Download Report as PDF"
   - Save to your computer

### Result Interpretation

#### Risk Levels
- 🔴 **CRITICAL**: 6+ vulnerabilities found
- 🟠 **HIGH**: 3-5 vulnerabilities found
- 🟡 **MEDIUM**: 1-2 vulnerabilities found
- 🟢 **LOW**: No vulnerabilities found

#### Severity Indicators
- **HIGH**: Immediately exploitable, critical fixes needed
- **MEDIUM**: Potential attack vector, should be addressed
- **LOW**: Minor issue, monitor for exploitation

## 🏗️ Project Structure

```
sqli_scanner/
│
├── backend/                          # Python scanning engine
│   ├── crawler.py                   # URL crawling & sitemap
│   ├── detector.py                  # SQL injection detection
│   ├── xss_detector.py              # XSS detection
│   ├── csrf_detector.py             # CSRF detection
│   ├── payloads.py                  # SQLi payloads
│   ├── xss_payloads.py              # XSS payloads
│   ├── csrf_payloads.py             # CSRF vectors
│   ├── utils.py                     # Utility functions
│   ├── scanner.py                   # Main scanner
│   └── requirements.txt              # Python dependencies
│
├── frontend/                         # React web interface
│   ├── src/
│   │   ├── components/              # React components
│   │   │   ├── URLInput.tsx
│   │   │   ├── VulnerabilityOptions.tsx
│   │   │   ├── VulnerabilityCheckbox.tsx
│   │   │   ├── VulnerabilityResults.tsx
│   │   │   ├── SitemapDisplay.tsx
│   │   │   ├── ScanReport.tsx
│   │   │   └── PDFGenerator.tsx
│   │   ├── services/                # API services
│   │   │   └── api.ts
│   │   ├── types/                   # TypeScript types
│   │   │   └── index.ts
│   │   ├── App.tsx                  # Main component
│   │   ├── main.tsx                 # Entry point
│   │   └── index.css                # Styles
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── tsconfig.json
│   ├── index.html
│   └── README.md
│
├── sitemap/                         # Generated sitemaps
│   └── sitemap_*.png               # Sitemap images
│
├── api.py                           # Flask API server
├── requirements-api.txt             # API dependencies
├── quickstart.bat                   # Quick start (Windows)
├── quickstart.sh                    # Quick start (Linux/macOS)
├── DEPLOYMENT_GUIDE.md              # Deployment instructions
├── CSRF_README.md                   # CSRF scanner docs
└── PROJECT_README.md                # This file
```

## 🛠️ Tech Stack

### Backend
- **Python 3.8+**: Core language
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin requests
- **Requests**: HTTP client
- **BeautifulSoup4**: HTML parsing
- **NetworkX**: Graph analysis
- **Matplotlib**: Visualization

### Frontend
- **React 18**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **Axios**: HTTP client
- **jsPDF**: PDF generation
- **html2canvas**: Screenshot to image
- **Lucide React**: Icons

## 🔐 Security Features

### Input Validation
- URL format validation
- Protocol verification (HTTP/HTTPS only)
- Payload sanitization

### API Security
- CORS configuration
- Input validation on all endpoints
- Error handling without sensitive info exposure

### Data Privacy
- No data persistence by default
- Results cleared after session
- HTTPS recommended for deployment

## 📊 API Endpoints

### POST /scan
```json
Request:
{
  "url": "https://example.com",
  "check_sqli": true,
  "check_xss": true,
  "check_csrf": true
}

Response:
{
  "url": "https://example.com",
  "timestamp": "2026-01-27T10:30:00Z",
  "vulnerabilities": {
    "sqli": [...],
    "xss": [...],
    "csrf": [...]
  },
  "sitemapData": {
    "urls": [...],
    "totalUrls": 15
  }
}
```

### GET /health
Returns: `{"status": "ok", "message": "Server is running"}`

### GET /info
Returns: API information and available endpoints

## ⚙️ Configuration

### Backend (api.py)
```python
app.run(
    debug=True,           # Disable in production
    host='0.0.0.0',      # Listen on all interfaces
    port=5000             # Change port as needed
)
```

### Frontend (src/services/api.ts)
```typescript
const API_BASE = 'http://localhost:5000';
timeout: 300000  // 5 minutes in milliseconds
```

### Scanning (backend/scanner.py)
```python
max_urls = 50        # Maximum URLs to crawl
timeout = 10         # Seconds per request
```

## 📈 Performance Tips

### For Large Sites
- Scan during off-peak hours
- Increase timeout values
- Reduce max_urls parameter
- Use targeted scanning

### Optimization
- Clear browser cache
- Close unused applications
- Use wired connection if possible
- Allocate sufficient RAM

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Cannot connect to API | Ensure `python api.py` is running |
| CORS errors | Check `CORS(app)` in api.py |
| Scan timeout | Increase timeout or reduce URL count |
| PDF download fails | Check browser permissions |
| High memory usage | Restart application |
| Slow scanning | Close background apps, check internet |

## 🚢 Deployment

### Local Testing
```bash
npm run dev       # Frontend dev server
python api.py     # Backend API
```

### Production Build
```bash
cd frontend
npm run build
npm run preview
```

### Docker Deployment
```bash
docker-compose up
```

### Cloud Deployment
- **Heroku**: See DEPLOYMENT_GUIDE.md
- **AWS**: See DEPLOYMENT_GUIDE.md
- **GCP**: See DEPLOYMENT_GUIDE.md
- **Azure**: See DEPLOYMENT_GUIDE.md

## 📚 Documentation

- [Frontend Setup Guide](frontend/SETUP_GUIDE.md)
- [Frontend README](frontend/README.md)
- [CSRF Scanner Details](CSRF_README.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

MIT License - See LICENSE file for details

## ⚠️ Disclaimer

This tool is designed for authorized security testing only. Unauthorized access to computer systems is illegal. Always obtain proper authorization before scanning any website or network.

## 🆘 Support

### Common Questions

**Q: How long does a typical scan take?**
A: 1-5 minutes depending on site size and internet speed

**Q: Can I scan multiple sites simultaneously?**
A: Currently supports sequential scanning; parallel in future versions

**Q: Does the tool store scan results?**
A: No, results are cleared after session by default

**Q: Can I integrate with other tools?**
A: Yes, API endpoints can be integrated with other applications

### Getting Help
1. Check troubleshooting section above
2. Review browser console (F12)
3. Check server logs (terminal)
4. Read documentation files
5. Contact development team

## 🔄 Updates & Changelog

### Version 1.0.0 (Current)
- Initial release
- SQLi, XSS, CSRF detection
- Modern React frontend
- PDF report generation
- Sitemap visualization

### Planned Features
- Database persistence
- Scan scheduling
- Team collaboration
- Advanced filtering
- Custom payloads
- API authentication

## 👨‍💻 Development Team

Created with ❤️ for web security professionals

## 📞 Contact

For issues, feature requests, or general inquiries:
- Email: support@example.com
- Issues: GitHub issues page
- Discussions: GitHub discussions

---

**Version**: 1.0.0  
**Last Updated**: January 27, 2026  
**Status**: Production Ready ✅

### Quick Links
- [Quick Start Guide](#-quick-start)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [API Endpoints](#-api-endpoints)
- [Troubleshooting](#-troubleshooting)
- [Deployment](#-deployment)

**Happy Scanning! 🔍🔐**
