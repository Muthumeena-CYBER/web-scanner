# Frontend Setup & Usage Guide

## Quick Start

### 1. Installation

```bash
cd frontend
npm install
```

### 2. Development Server

```bash
npm run dev
```

The application will open at `http://localhost:3000`

### 3. Build for Production

```bash
npm run build
npm run preview
```

## Features Overview

### 1. URL Input Field
- Enter target URL for scanning
- Real-time validation
- Error feedback for invalid URLs

### 2. Vulnerability Selection
- **SQL Injection (SQLi)**: Detect SQL injection vulnerabilities
- **Cross-Site Scripting (XSS)**: Identify reflected XSS issues
- **Cross-Site Request Forgery (CSRF)**: Find CSRF weaknesses
- All three are enabled by default

### 3. Scanning Process
1. Enter URL
2. Select vulnerability types to check
3. Click "Start Scan"
4. Wait for results (can take up to 5 minutes)
5. View detailed results and sitemap

### 4. Results Display
- **Sitemap**: Visual representation of discovered URLs
- **Vulnerability Cards**: Color-coded findings by type
- **Severity Badges**: HIGH, MEDIUM, LOW severity indicators
- **Detailed Info**: Payload, parameters, and technical details

### 5. PDF Report Generation
- **Download Button**: Export scan results as PDF
- **Professional Format**: Neat, formal layout
- **Auto-naming**: Filename includes domain and date
- **High Quality**: 2x scale, 300 DPI

## UI Components

### Header
- Logo with application name
- Tagline: "Comprehensive Vulnerability Detection"

### Input Section
- URL input with validation
- Vulnerability checkboxes (default all selected)
- Start button with loading indicator

### Results Section (3-column layout)
- **SQL Injection Panel**: Blue theme (#6366F1)
- **XSS Panel**: Pink theme (#EC4899)
- **CSRF Panel**: Amber theme (#F59E0B)

### Full Report
- Professional report format
- Risk level assessment
- Summary statistics
- Detailed findings per vulnerability type

### Sitemap Visualization
- Hierarchical URL structure
- Color-coded nodes
- Connection mapping

## Color Coding

| Component | Color | Hex |
|-----------|-------|-----|
| Primary | Indigo | #6366F1 |
| Secondary | Pink | #EC4899 |
| Accent | Teal | #14B8A6 |
| SQL Injection | Blue | #6366F1 |
| XSS | Pink | #EC4899 |
| CSRF | Amber | #F59E0B |
| Danger/Critical | Red | #EF4444 |
| Success | Green | #10B981 |

## API Endpoints

The frontend connects to backend at `http://localhost:5000`

### Endpoint: POST /scan
Initiates a security scan on the provided URL.

**Request:**
```json
{
  "url": "https://example.com",
  "check_sqli": true,
  "check_xss": true,
  "check_csrf": true
}
```

**Response:**
```json
{
  "url": "https://example.com",
  "timestamp": "2026-01-27T10:30:00Z",
  "vulnerabilities": {
    "sqli": [
      {
        "param": "id",
        "payload": "1 OR 1=1",
        "type": "Boolean-based"
      }
    ],
    "xss": [],
    "csrf": []
  },
  "sitemapData": {
    "urls": ["https://example.com/page1", "..."],
    "totalUrls": 15,
    "sitemapImage": "base64_image_data"
  }
}
```

## Troubleshooting

### Issue: Cannot connect to backend
- Ensure backend is running on `http://localhost:5000`
- Check firewall settings
- Verify no port conflicts

### Issue: Scan times out
- Increase timeout in `src/services/api.ts` (currently 5 minutes)
- Try smaller websites first
- Check network connectivity

### Issue: PDF download fails
- Ensure html2canvas and jsPDF are installed
- Check browser permissions for downloads
- Try a different browser

## Keyboard Shortcuts

- `Enter` - Submit URL for scanning
- `Tab` - Navigate between checkboxes and buttons

## Responsive Design

- Desktop (1200px+): 3-column layout
- Tablet (768px-1199px): 2-column layout
- Mobile (< 768px): Single column stack

## Performance Tips

1. Limit scanning to smaller websites initially
2. Disable checks you don't need
3. Use modern browsers for best performance
4. Clear browser cache if issues occur

## Browser Compatibility

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Supported |
| Firefox | 88+ | ✅ Supported |
| Safari | 14+ | ✅ Supported |
| Edge | 90+ | ✅ Supported |
| IE 11 | - | ❌ Not supported |

## Environment Variables

Create `.env.local` in frontend folder (optional):

```
VITE_API_URL=http://localhost:5000
VITE_TIMEOUT=300000
```

## Building & Deployment

### Local Build
```bash
npm run build
npm run preview
```

### Deployment Options
- **Vercel**: Optimized for React/Vite
- **Netlify**: Simple drag-and-drop deployment
- **GitHub Pages**: Static hosting
- **AWS S3**: With CloudFront
- **Docker**: Containerized deployment

### Docker Build
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

## Maintenance

- Regular npm updates: `npm update`
- Security audits: `npm audit`
- Dependency checks: `npm outdated`

## Support & Contact

For issues, feature requests, or questions:
- Check the README.md
- Review error messages in browser console
- Contact development team

---

**Version**: 1.0.0  
**Last Updated**: January 27, 2026
