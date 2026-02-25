# Web Security Scanner

A full-stack web security scanner for identifying common web vulnerabilities and generating reports.

## What this project is

This project scans a target website for:
- SQL Injection (SQLi)
- Cross-Site Scripting (XSS)
- Cross-Site Request Forgery (CSRF)
- Full TCP Port Scanning (1-65535)

It includes:
- Python + Flask backend scanner API
- React + TypeScript frontend dashboard
- PDF report generation
- Automatic JSON report generation after each scan
- Sitemap visualization
- Scan history storage
- Async scan progress with scan phases (web scan, port scan, finalizing)

## Tech stack

- Backend: Python, Flask, BeautifulSoup, requests, networkx, matplotlib
- Frontend: React, TypeScript, Vite, Tailwind CSS

## Project structure

```text
sqli_scanner/
  backend/              # Scanner engine and Flask API implementation
  frontend/             # React app
  sitemap/              # Generated sitemap images
  pdfs/                 # Generated reports
  scan_history/         # Stored scan history
  api.py                # Root API runner (loads backend/api.py)
  requirements-api.txt
```

## Prerequisites

- Python 3.9+
- Node.js 18+ (Node 16 may work, but 18+ is recommended)
- npm

## Setup

### 1) Clone and enter project

```bash
cd sqli_scanner
```

### 2) Backend setup

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r backend/requirements.txt
pip install -r requirements-api.txt
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
pip install -r requirements-api.txt
```

### 3) Frontend setup

```bash
cd frontend
npm install
cd ..
```

## Run the project

Open two terminals from `sqli_scanner/`.

### Terminal 1: Run backend

Activate virtual environment, then:

```bash
python api.py
```

Backend runs at:
- `http://127.0.0.1:5000`

### Terminal 2: Run frontend

```bash
cd frontend
npm run dev
```

Frontend runs at:
- `http://localhost:3000`

The frontend is configured to proxy `/api` calls to the backend on port `5000`.

## Addons implemented

- Full TCP port scanner module in [backend/port_scanner.py](backend/port_scanner.py)
  - Scans all ports `1..65535`
  - Uses `socket` + `ThreadPoolExecutor` (no nmap)
  - Service guessing for common ports
  - Risk classification (`Low`/`Medium`/`High`)
  - Safety warning + authorization gating for non-test targets
- Port scan integrated into main scan response and report
  - `port_scan_results` included in API response
  - `overall_risk_score` combines web risk + port risk
- Improved async progress tracking
  - URL scanning progress
  - Port scanning progress (`currentPort` / `totalPorts`)
  - Phase messages for better UI feedback
- Automatic JSON report generation
  - Report is generated automatically after scan completion
  - Saved in `pdfs/report_*.json`
- URL handling improvements
  - Accepts input with or without protocol (`example.com` or `https://example.com`)
  - Normalizes and validates URL server-side
- Crawler reliability fixes
  - Start URL always included in scan targets
  - Relative links resolved against current page URL
  - Non-GUI matplotlib backend (`Agg`) to avoid tkinter thread crashes

## Build frontend for production

```bash
cd frontend
npm run build
npm run preview
```

## Quick health check

After starting backend:

```bash
curl http://127.0.0.1:5000/health
```

Expected: JSON response indicating the server is running.

## Core API fields (scan response)

`POST /scan` and `POST /scan/async` now include:

- `web_vulnerabilities`
- `port_scan_results`
- `overall_risk_score`
- `report_generated`
- `report_filename` (when report generation succeeds)

## Common issues

- Port already in use:
  - Stop processes using `3000` or `5000`, then restart.
- Python dependency install fails:
  - Ensure the virtual environment is active.
  - Upgrade pip and retry.
- Frontend cannot reach backend:
  - Confirm backend is running on `127.0.0.1:5000`.
  - Confirm frontend started from `frontend/` with `npm run dev`.

## Notes

- Scan outputs are saved under `sitemap/`, `pdfs/`, and `scan_history/`.
- Use this tool only on systems you own or are authorized to test.
