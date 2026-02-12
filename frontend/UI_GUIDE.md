# Frontend UI Components Guide

## 📐 Layout Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       Header Section                             │
│  [Shield Icon] Web Security Scanner - Comprehensive Detection    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Input Section                               │
├─────────────────────────────────────────────────────────────────┤
│  Target URL                                                      │
│  [🔍 https://example.com_________________]                      │
│                                                                  │
│  Vulnerability Checks  [▼ Expand/Collapse]                     │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐│
│  │ ☑ SQL Injection  │ │ ☑ XSS           │ │ ☑ CSRF          ││
│  │ Detect SQLi...   │ │ Identify XSS... │ │ Detect missing..││
│  └──────────────────┘ └──────────────────┘ └──────────────────┘│
│                                                                  │
│  [🔍 Start Scan]  (or loading indicator: ⟳ Scanning...)        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  Sitemap Section                                 │
├─────────────────────────────────────────────────────────────────┤
│  [🗺] Sitemap Overview                                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                                                           │  │
│  │        [Visual Sitemap Graph Image]                      │  │
│  │        (Hierarchical URL structure)                      │  │
│  │                                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Total URLs Discovered: 15                                      │
│  URLs Found:                                                    │
│  • https://example.com/                                         │
│  • https://example.com/about                                    │
│  • ... and 13 more URLs                                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────┬────────────────────────────────────────┬──────────────────────────────┐
│      SQL Injection Panel              │      XSS Panel                          │      CSRF Panel               │
├──────────────────────────────────────┼────────────────────────────────────────┼──────────────────────────────┤
│ SQL Injection                         │ Cross-Site Scripting                    │ CSRF                         │
│                                       │                                         │                              │
│ ✓ No vulnerabilities                  │ ⚠ 2 XSS Found                           │ ✓ No vulnerabilities         │
│   detected                            │                                         │   detected                   │
│                                       │ ┌──────────────────────────────────┐   │                              │
│                                       │ │ search                           │   │                              │
│                                       │ │ Type: Reflected XSS              │   │                              │
│                                       │ │ Payload: <img src=x onerror=a>  │   │                              │
│                                       │ │                                  │   │                              │
│                                       │ │ HIGH                             │   │                              │
│                                       │ └──────────────────────────────────┘   │                              │
│                                       │                                         │                              │
│                                       │ ┌──────────────────────────────────┐   │                              │
│                                       │ │ comment                          │   │                              │
│                                       │ │ Type: Reflected XSS              │   │                              │
│                                       │ │ Payload: <script>alert(1)</scr...│   │                              │
│                                       │ │                                  │   │                              │
│                                       │ │ HIGH                             │   │                              │
│                                       │ └──────────────────────────────────┘   │                              │
└──────────────────────────────────────┴────────────────────────────────────────┴──────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   Full Scan Report                               │
├─────────────────────────────────────────────────────────────────┤
│  Security Scan Report                                       🔴 CRITICAL
│                                                                  │
│  Target Information:                                             │
│  URL: https://example.com                                       │
│  Scan Date: 2026-01-27 10:30:00                                 │
│                                                                  │
│  Summary:                                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ SQL Injections: 0  │  XSS Issues: 2  │  CSRF Issues: 1  │   │
│  │ Total Issues: 3                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  [Detailed findings...]                                         │
│  [PDF Report Content Preview]                                   │
│                                                                  │
│  [📄 Download Report as PDF]                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         Footer                                   │
│  Web Security Scanner v1.0 | Comprehensive Vulnerability...    │
└─────────────────────────────────────────────────────────────────┘
```

## 🎨 Color Scheme

### Vulnerability Types
```
SQL Injection (SQLi)
  Primary: #6366F1 (Indigo)
  Background: #E0E7FF
  
Cross-Site Scripting (XSS)
  Primary: #EC4899 (Pink)
  Background: #FCE7F3
  
CSRF (CSRF)
  Primary: #F59E0B (Amber)
  Background: #FEF3C7
```

### Severity Badges
```
HIGH
  Icon: AlertOctagon
  Color: #DC2626 (Red)
  Background: #FEE2E2
  
MEDIUM
  Icon: AlertTriangle
  Color: #EA580C (Orange)
  Background: #FFEDD5
  
LOW
  Icon: AlertCircle
  Color: #16A34A (Green)
  Background: #DCFCE7
```

### Status States
```
🟢 No vulnerabilities found - Green theme
🟡 Low risk (1-2 findings) - Yellow/Amber theme
🟠 Medium risk (3-5 findings) - Orange theme
🔴 High/Critical risk (6+ findings) - Red theme
```

## 🧩 Component Hierarchy

```
App (Main Container)
├── Header
│   └── Logo + Title
├── Main Content
│   ├── Input Section
│   │   ├── URLInput
│   │   │   └── [URL Input Field]
│   │   └── VulnerabilityOptions
│   │       ├── VulnerabilityCheckbox (SQLi)
│   │       ├── VulnerabilityCheckbox (XSS)
│   │       └── VulnerabilityCheckbox (CSRF)
│   │
│   ├── Error Display (conditional)
│   │   └── [Error Message]
│   │
│   └── Results Section (conditional)
│       ├── SitemapDisplay
│       │   ├── [Sitemap Image]
│       │   ├── URL Count Badge
│       │   └── URLs List
│       │
│       ├── Vulnerabilities Grid (3 columns)
│       │   ├── SQLi Results
│       │   │   └── VulnerabilityResults
│       │   ├── XSS Results
│       │   │   └── VulnerabilityResults
│       │   └── CSRF Results
│       │       └── VulnerabilityResults
│       │
│       ├── Full Report
│       │   └── ScanReport
│       │       ├── Report Header
│       │       ├── Target Info
│       │       ├── Summary Stats
│       │       └── Detailed Findings
│       │
│       └── PDF Button
│           └── PDFGenerator
│
└── Footer
    └── Copyright + Info
```

## 📱 Responsive Breakpoints

```
Desktop (1200px+)
├── 3-column vulnerability grid
├── Full-width content
└── Sidebar (potential future)

Tablet (768px - 1199px)
├── 2-column vulnerability grid
├── Adjusted spacing
└── Mobile menu

Mobile (< 768px)
├── Single column stack
├── Full-width components
└── Hamburger menu (potential)
```

## ⌚ Loading States

### URL Input Loading
```
Normal: [🔍 Start Scan]
Loading: [⟳ Scanning...] (disabled, gray background)
```

### Results Loading
```
Initial: "Ready to scan" message with icon
Loading: Spinner animation with progress text
Success: Display all results
Error: Error message with retry option
```

## 🔄 State Transitions

```
Initial State
    ↓
User enters URL
    ↓
User selects vulnerabilities (default all selected)
    ↓
User clicks "Start Scan"
    ↓ (validation)
Loading State
    ↓ (scanning progress)
Results Display
    ├─→ Sitemap View
    ├─→ 3-Panel Results View
    ├─→ Full Report View
    └─→ PDF Download Option
    ↓
User can download PDF
    ↓
User can start new scan
```

## 🎯 User Flows

### Successful Scan Flow
```
1. Enter URL → 2. Check boxes (pre-selected) → 3. Click Scan
      ↓
4. Wait for scan → 5. View sitemap → 6. Review vulnerabilities
      ↓
7. Read full report → 8. Download PDF → Done
```

### Error Handling Flow
```
Invalid URL Input → Show validation error → Highlight field → User corrects
      ↓
Failed Scan → Show error message → Option to retry
      ↓
PDF Generation Error → Show error → Allow retry
```

## 🎨 Typography

### Headings
- H1: 28px, Bold, Primary Color
- H2: 24px, Bold, Gray-900
- H3: 20px, Semibold, Gray-900
- H4: 18px, Semibold, Gray-900

### Body Text
- Regular: 16px, Regular, Gray-700
- Small: 14px, Regular, Gray-600
- Tiny: 12px, Regular, Gray-500

### Code/Payload
- Font: Monospace
- Size: 12px
- Background: Subtle gray
- Truncation: After 50 chars with ellipsis

## 📐 Spacing

```
Extra Large: 32px (sections)
Large: 24px (components)
Medium: 16px (elements)
Small: 8px (minor elements)
Tiny: 4px (details)
```

## 🔘 Button Styles

### Primary Button
```
Background: Indigo (#6366F1)
Text: White
Padding: 12px 24px
Border Radius: 8px
Hover: Darker shade
Active: Scale down (95%)
Disabled: Gray, cursor: not-allowed
```

### Secondary Button
```
Background: Gradient (Primary → Secondary)
Text: White
Shadow: Active on hover
```

### Checkbox Style
```
Size: 20px × 20px
Checked: Indigo background
Unchecked: Gray border
Focus: Ring around checkbox
```

## 🌙 Dark Mode (Future)

```
Background: #1F2937 (Dark gray)
Surface: #111827 (Darker)
Text: #F3F4F6 (Light gray)
Accent: #818CF8 (Light indigo)
```

## ♿ Accessibility

- Color contrast ratio: 4.5:1 minimum
- Focus visible on all interactive elements
- Semantic HTML structure
- ARIA labels where needed
- Keyboard navigation support
- Screen reader friendly

---

**Last Updated**: January 27, 2026
