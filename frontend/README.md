# Web Security Scanner - Frontend

A modern, responsive web application for comprehensive web vulnerability scanning and reporting.

## Features

- 🎯 **URL-based Scanning**: Enter any target URL to scan for vulnerabilities
- 🔒 **Three Vulnerability Types**: SQL Injection, XSS, and CSRF detection
- 🗺️ **Sitemap Visualization**: See the site structure of discovered URLs
- 📊 **Detailed Results**: Color-coded vulnerability findings with severity levels
- 📄 **PDF Reports**: Generate professional, downloadable security reports
- 🎨 **Modern UI**: Beautiful, responsive design with Tailwind CSS
- ⚡ **Real-time Feedback**: Live scanning status and error handling

## Tech Stack

- **React 18** - Modern UI library
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Vite** - Lightning-fast build tool
- **Axios** - HTTP client for API communication
- **jsPDF & html2canvas** - PDF generation
- **Lucide React** - Beautiful icons

## Installation

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The frontend will run on `http://localhost:3000` by default.

## File Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── URLInput.tsx              # URL input field with validation
│   │   ├── VulnerabilityOptions.tsx  # Checkbox selectors for SQLi/XSS/CSRF
│   │   ├── VulnerabilityCheckbox.tsx # Individual checkbox component
│   │   ├── VulnerabilityResults.tsx  # Results display for each vuln type
│   │   ├── SitemapDisplay.tsx        # Sitemap visualization
│   │   ├── ScanReport.tsx            # Detailed scan report
│   │   └── PDFGenerator.tsx          # PDF export functionality
│   ├── services/
│   │   └── api.ts                    # Backend API communication
│   ├── types/
│   │   └── index.ts                  # TypeScript type definitions
│   ├── App.tsx                       # Main application component
│   ├── main.tsx                      # React entry point
│   └── index.css                     # Global styles
├── package.json
├── vite.config.ts                    # Vite configuration
├── tsconfig.json                     # TypeScript configuration
├── tailwind.config.js                # Tailwind CSS configuration
├── postcss.config.js                 # PostCSS configuration
└── index.html                        # HTML entry point
```

## Configuration

### Backend API

The frontend communicates with the backend via HTTP. Configure the API endpoint in `src/services/api.ts`:

```typescript
const API_BASE = 'http://localhost:5000';
```

### Tailwind CSS

Customize colors and themes in `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: '#6366F1',
      secondary: '#EC4899',
      accent: '#14B8A6',
    },
  },
}
```

## Components Overview

### URLInput
- URL validation
- Input field with search icon
- Error messages
- Loading state

### VulnerabilityOptions
- Three toggles for SQLi, XSS, CSRF
- Default selected (all enabled)
- Expandable section
- Descriptions for each vulnerability type

### VulnerabilityResults
- Color-coded by vulnerability type
- Severity badges (HIGH, MEDIUM, LOW)
- Detailed information display
- Empty state when no vulnerabilities found

### ScanReport
- Professional formatted report
- Risk level assessment
- Summary statistics
- Detailed findings per vulnerability type
- Sitemap information

### PDFGenerator
- Converts report to PDF
- High-quality export (2x scale, 300 dpi)
- Auto-downloaded with timestamp
- Professional formatting

## API Integration

The frontend expects the backend to provide these endpoints:

### POST `/scan`
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
    "totalUrls": 15,
    "sitemapImage": "..."
  }
}
```

### GET `/sitemap`
```
Parameters: url (query param)
Response: Sitemap data
```

### GET `/download-pdf`
```
Parameters: url (query param)
Response: PDF file (blob)
```

## Styling

The application uses Tailwind CSS with a custom color palette:

- **Primary**: Indigo (#6366F1)
- **Secondary**: Pink (#EC4899)
- **Accent**: Teal (#14B8A6)
- **Danger**: Red (#EF4444)
- **Warning**: Amber (#F59E0B)
- **Success**: Green (#10B981)

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Development Tips

1. **Hot Module Replacement**: Changes are reflected instantly during development
2. **TypeScript**: Full type safety with strict mode enabled
3. **Tailwind Intellisense**: Install VS Code extension for better DX
4. **React DevTools**: Install browser extension for debugging

## Performance

- Vite provides ultra-fast HMR
- Code splitting for optimized bundle
- Lazy loading of components
- Optimized images and assets

## Error Handling

- Network errors are caught and displayed to users
- Invalid URLs are validated before submission
- API timeouts are handled (5-minute limit for scanning)
- User-friendly error messages

## Building for Production

```bash
npm run build
```

Outputs to `dist/` folder, ready for deployment.

## License

MIT

## Support

For issues or feature requests, please contact the development team.
