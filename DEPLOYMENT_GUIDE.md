# Complete Project Setup & Deployment Guide

## Project Structure Overview

```
sqli_scanner/
├── backend/                    # Python scanning engine
│   ├── crawler.py             # URL crawling & sitemap generation
│   ├── detector.py            # SQL Injection detection
│   ├── xss_detector.py        # XSS detection
│   ├── csrf_detector.py       # CSRF detection
│   ├── payloads.py            # SQL injection payloads
│   ├── xss_payloads.py        # XSS payloads
│   ├── csrf_payloads.py       # CSRF attack vectors
│   ├── utils.py               # Utility functions
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # React web interface
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API communication
│   │   ├── types/             # TypeScript definitions
│   │   ├── App.tsx            # Main component
│   │   └── index.css          # Styles
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── README.md
│
├── sitemap/                   # Generated sitemaps
│   └── sitemap_*.png          # Sitemap images
│
├── api.py                     # Flask API server
├── requirements-api.txt       # API dependencies
└── DEPLOYMENT_GUIDE.md        # This file
```

## Installation & Setup

### Step 1: Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn
- Git (optional)

### Step 2: Backend Setup

```bash
# Navigate to project root
cd sqli_scanner

# Install Python dependencies
pip install -r backend/requirements.txt
pip install -r requirements-api.txt
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Verify installation
npm list
```

### Step 4: Start Development Environment

#### Terminal 1 - Start Backend API
```bash
cd sqli_scanner
python api.py
```
Expected output:
```
[+] Web Security Scanner API Starting...
[+] Server running on http://localhost:5000
[+] CORS enabled for http://localhost:3000
```

#### Terminal 2 - Start Frontend
```bash
cd sqli_scanner/frontend
npm run dev
```
Expected output:
```
  VITE v5.0.8  ready in 123 ms

  ➜  Local:   http://localhost:3000/
  ➜  press h to show help
```

#### Terminal 3 - Monitor Backend (Optional)
```bash
cd sqli_scanner
tail -f backend/scanner.log  # If logging is enabled
```

### Step 5: Verify Installation

1. Open browser to `http://localhost:3000`
2. Check API health at `http://localhost:5000/health`
3. Expected response: `{"status":"ok","message":"Server is running"}`

## Usage Guide

### Basic Workflow

1. **Enter Target URL**
   - Example: `https://example.com`
   - Must be valid HTTP/HTTPS URL

2. **Select Vulnerability Types**
   - SQL Injection (SQLi) - Default: ✓
   - Cross-Site Scripting (XSS) - Default: ✓
   - Cross-Site Request Forgery (CSRF) - Default: ✓

3. **Start Scan**
   - Click "Start Scan" button
   - Monitor progress (can take 1-5 minutes)

4. **Review Results**
   - Sitemap: Visual structure of discovered URLs
   - Vulnerabilities: Color-coded by type and severity
   - Risk Level: Overall assessment (CRITICAL/HIGH/MEDIUM/LOW)

5. **Generate Report**
   - Review full formatted report
   - Click "Download Report as PDF"
   - Save to local system

### Output Files

Generated files are stored in:
- **Sitemaps**: `sqli_scanner/sitemap/sitemap_*.png`
- **Database**: Results saved in memory during scan
- **Reports**: Downloaded as PDF via browser

## Configuration

### API Configuration

Edit `api.py` to customize:

```python
# Change port
app.run(host='0.0.0.0', port=8080)

# Disable debug mode in production
app.run(debug=False)

# Change CORS allowed origins
CORS(app, resources={
    r"/*": {"origins": ["http://localhost:3000", "https://yourdomain.com"]}
})
```

### Frontend Configuration

Edit `frontend/src/services/api.ts`:

```typescript
const API_BASE = 'http://localhost:5000';  // Change API URL
timeout: 300000,  // Timeout in milliseconds (5 minutes default)
```

### Backend Configuration

Modify scanning parameters in `backend/detector.py` and `backend/scanner.py`:

```python
max_urls = 50  # Maximum URLs to scan per site
timeout = 10   # Timeout per request in seconds
```

## Production Deployment

### Option 1: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements*.txt ./
RUN pip install -r requirements-api.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run API
CMD ["python", "api.py"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=0

  frontend:
    image: node:18
    working_dir: /app
    volumes:
      - ./frontend:/app
    ports:
      - "3000:3000"
    command: npm run dev
```

Run with Docker:
```bash
docker-compose up
```

### Option 2: Cloud Deployment (Heroku)

```bash
# Install Heroku CLI
npm install -g heroku

# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set buildpack
heroku buildpacks:add heroku/python -a your-app-name
heroku buildpacks:add heroku/nodejs -a your-app-name

# Deploy
git push heroku main

# Check logs
heroku logs --tail -a your-app-name
```

### Option 3: AWS Deployment

**Backend (API)**:
1. Use AWS Elastic Beanstalk for Flask
2. Configure environment variables
3. Set up RDS for data persistence (optional)

**Frontend**:
1. Build: `npm run build`
2. Upload `dist/` to S3
3. Distribute via CloudFront

### Option 4: Traditional Server Deployment

#### Using Gunicorn + Nginx

```bash
# Install Gunicorn
pip install gunicorn

# Run API with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api:app
```

Nginx configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/frontend/dist;
    }
}
```

## Performance Optimization

### Backend Optimization
- Implement caching for repeated scans
- Use connection pooling
- Add request rate limiting
- Optimize database queries

### Frontend Optimization
```bash
# Build optimized bundle
npm run build

# Check bundle size
npm run preview
```

### Network Optimization
- Enable gzip compression
- Use CDN for static assets
- Implement lazy loading
- Minify CSS/JS

## Security Considerations

### Backend Security
```python
# Use environment variables for sensitive data
import os
API_KEY = os.environ.get('API_KEY')

# Validate all inputs
if not is_valid_url(url):
    return error_response()

# Use HTTPS in production
app.run(ssl_context='adhoc')

# Set security headers
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

### Frontend Security
- Validate URLs before submission
- Sanitize API responses
- Use HTTPS for all communications
- Store sensitive data securely

### CORS Configuration
```python
# Restrict to specific origins in production
CORS(app, 
    origins=['https://yourdomain.com'],
    allow_headers=['Content-Type'],
    methods=['GET', 'POST']
)
```

## Monitoring & Logging

### Backend Logging
```python
import logging

logging.basicConfig(
    filename='scanner.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"Scan started for {url}")
```

### Performance Monitoring
- Track scan duration
- Monitor API response times
- Track error rates
- Use APM tools (New Relic, DataDog)

## Troubleshooting

### Issue: "Cannot GET http://localhost:5000/scan"
**Solution**: Ensure backend API is running with `python api.py`

### Issue: CORS errors in browser console
**Solution**: Verify `CORS(app)` in api.py and check allowed origins

### Issue: Scan times out
**Solution**: Increase timeout in `src/services/api.ts` or reduce max_urls in backend

### Issue: PDF download fails
**Solution**: Clear browser cache, try different browser, check browser permissions

### Issue: Memory usage grows continuously
**Solution**: Implement result caching with TTL, add garbage collection

## API Endpoints Reference

### POST /scan
Initiates security scan
- **URL**: `http://localhost:5000/scan`
- **Method**: POST
- **Content-Type**: application/json
- **Timeout**: 5 minutes

### GET /health
Health check
- **URL**: `http://localhost:5000/health`
- **Method**: GET

### GET /info
API information
- **URL**: `http://localhost:5000/info`
- **Method**: GET

## Database Schema (Future)

When implementing data persistence:

```sql
CREATE TABLE scans (
    id INTEGER PRIMARY KEY,
    url VARCHAR(255),
    timestamp DATETIME,
    status VARCHAR(50),
    result JSON
);

CREATE TABLE vulnerabilities (
    id INTEGER PRIMARY KEY,
    scan_id INTEGER,
    type VARCHAR(50),
    severity VARCHAR(20),
    details JSON,
    FOREIGN KEY (scan_id) REFERENCES scans(id)
);
```

## Scaling Considerations

### Load Balancing
```
Client -> Load Balancer (Nginx)
         ├-> API Instance 1
         ├-> API Instance 2
         └-> API Instance 3
```

### Caching Strategy
- Cache scan results for 24 hours
- Cache URL patterns
- Use Redis for distributed caching

### Database Replication
- Master-slave setup for MySQL
- MongoDB replica sets
- Backup strategy

## Backup & Recovery

### Daily Backups
```bash
# Backup sitemaps
tar -czf backups/sitemap_$(date +%Y%m%d).tar.gz sitemap/

# Backup database (if using)
mysqldump -u user -p database > backups/db_$(date +%Y%m%d).sql
```

### Recovery
```bash
# Restore from backup
tar -xzf backups/sitemap_20260127.tar.gz
mysql -u user -p database < backups/db_20260127.sql
```

## Testing

### Backend Testing
```bash
# Run tests
python -m pytest backend/tests/

# With coverage
pytest --cov=backend tests/
```

### Frontend Testing
```bash
# Run tests
npm run test

# With coverage
npm run test -- --coverage
```

### End-to-End Testing
```bash
# Using Cypress
npm run cypress:open
```

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs in browser console and backend output
3. Contact development team
4. Open GitHub issue

---

**Last Updated**: January 27, 2026  
**Version**: 1.0.0  
**Status**: Production Ready
