import React from 'react';
import { Download, File } from 'lucide-react';
import { jsPDF } from 'jspdf';
import { ScanResult, VulnerabilityFinding } from '../types';

interface PDFGeneratorProps {
  url: string;
  results: ScanResult;
  onDownload?: () => void;
  label?: string;
}

type Severity = 'Critical' | 'High' | 'Medium' | 'Low';
type RGB = [number, number, number];

const SEVERITY_ORDER: Severity[] = ['Critical', 'High', 'Medium', 'Low'];

const COLORS = {
  text: [31, 41, 55] as RGB,
  title: [15, 23, 42] as RGB,
  summaryBoxFill: [224, 242, 254] as RGB,
  summaryBoxBorder: [3, 105, 161] as RGB,
  tableHeaderFill: [235, 244, 255] as RGB,
  tableHeaderText: [30, 58, 138] as RGB,
  tableBorder: [209, 213, 219] as RGB,
  modules: {
    sqli: [185, 28, 28] as RGB,
    xss: [194, 65, 12] as RGB,
    csrf: [29, 78, 216] as RGB,
  },
};

const getHostname = (targetUrl: string): string => {
  try {
    return new URL(targetUrl).hostname;
  } catch {
    return targetUrl;
  }
};

const formatDate = (iso?: string): string => {
  if (!iso) return '-';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? '-' : d.toLocaleDateString('en-US');
};

const formatTime = (iso?: string): string => {
  if (!iso) return '-';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? '-' : d.toLocaleTimeString('en-US');
};

const formatDuration = (seconds?: number): string => {
  if (!seconds || seconds < 0) return '-';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
};

const toSeverity = (vuln: VulnerabilityFinding, fallback: Severity): Severity => {
  const raw = (vuln.severity || '').toLowerCase();
  if (raw.includes('critical')) return 'Critical';
  if (raw.includes('high')) return 'High';
  if (raw.includes('medium')) return 'Medium';
  if (raw.includes('low')) return 'Low';
  return fallback;
};

const detectXssType = (vuln: VulnerabilityFinding): string => {
  const raw = (vuln.type || vuln.vulnerability_type || '').toLowerCase();
  if (raw.includes('stored')) return 'Stored XSS';
  if (raw.includes('dom')) return 'DOM-based XSS';
  return 'Reflected XSS';
};

const getHighestSeverity = (values: Severity[]): Severity => {
  for (const s of SEVERITY_ORDER) {
    if (values.includes(s)) return s;
  }
  return 'Low';
};

const overallRiskFromCounts = (severityCounts: Record<Severity, number>): Severity => {
  if (severityCounts.Critical > 0) return 'Critical';
  if (severityCounts.High > 0) return 'High';
  if (severityCounts.Medium > 0) return 'Medium';
  return 'Low';
};

const sanitizeText = (value: string): string => value.replace(/[^\x20-\x7E]/g, '').trim();

export const PDFGenerator: React.FC<PDFGeneratorProps> = ({ url, results, onDownload, label = 'Download PDF' }) => {
  const handleGeneratePDF = () => {
    try {
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = 210;
      const pageHeight = 297;
      const margin = 14;
      const contentWidth = pageWidth - margin * 2;
      let y = margin;

      const sqli = results.vulnerabilities?.sqli || [];
      const xss = results.vulnerabilities?.xss || [];
      const csrf = results.vulnerabilities?.csrf || [];
      const totalUrls = results.sitemapData?.totalUrls ?? results.sitemap_urls?.length ?? 0;
      const totalVulns = sqli.length + xss.length + csrf.length;

      const sqliSeverities = sqli.map((v) => toSeverity(v, 'Critical'));
      const xssSeverities = xss.map((v) => toSeverity(v, 'High'));
      const csrfSeverities = csrf.map((v) => toSeverity(v, 'Medium'));
      const allSeverities = [...sqliSeverities, ...xssSeverities, ...csrfSeverities];

      const severityCounts: Record<Severity, number> = {
        Critical: allSeverities.filter((s) => s === 'Critical').length,
        High: allSeverities.filter((s) => s === 'High').length,
        Medium: allSeverities.filter((s) => s === 'Medium').length,
        Low: allSeverities.filter((s) => s === 'Low').length,
      };

      const overallRisk = overallRiskFromCounts(severityCounts);

      const scanStart = results.scan_start_time || results.timestamp;
      const scanEnd = results.scan_end_time || results.timestamp;
      const durationSeconds = results.scan_duration_seconds;

      const totalRequestsSent = results.performance?.total_requests_sent ?? (totalUrls * 3);
      const totalResponsesReceived = results.performance?.total_responses_received ?? totalRequestsSent;
      const totalFormsDetected =
        results.performance?.total_forms_detected ??
        new Set(csrf.map((v) => v.formName).filter(Boolean)).size;
      const totalParamsTested =
        results.performance?.total_input_parameters_tested ??
        new Set([...sqli, ...xss].map((v) => v.parameter || v.param).filter(Boolean)).size;
      const averageResponseTime = results.performance?.average_response_time_ms ?? 0;
      const scanMode = results.performance?.scan_mode || 'Async';
      const threadCount = results.performance?.thread_count_used ?? 1;
      const errorsEncountered = results.performance?.errors_encountered ?? 0;
      const serverType = results.server?.type || 'Unknown';

      const payloadEntries =
        results.performance?.payload_metrics?.entries ||
        [
          ...sqli.map((v) => ({
            vulnerabilityType: 'SQL Injection' as const,
            payloadUsed: v.payload || '-',
            status: 'Successful' as const,
            responseCode: '200',
          })),
          ...xss.map((v) => ({
            vulnerabilityType: 'Cross-Site Scripting' as const,
            payloadUsed: v.payload || '-',
            status: 'Successful' as const,
            responseCode: '200',
          })),
          ...csrf.map(() => ({
            vulnerabilityType: 'CSRF' as const,
            payloadUsed: 'Form security test',
            status: 'Detected' as const,
            responseCode: '200',
          })),
        ];

      const totalPayloadsTested =
        results.performance?.payload_metrics?.total_payloads_tested ?? payloadEntries.length;
      const successfulPayloads =
        results.performance?.payload_metrics?.successful_payloads ??
        payloadEntries.filter((p) => p.status !== 'Blocked').length;
      const blockedPayloads =
        results.performance?.payload_metrics?.blocked_payloads ??
        payloadEntries.filter((p) => p.status === 'Blocked').length;

      const setTextColor = (color: RGB) => {
        pdf.setTextColor(color[0], color[1], color[2]);
      };

      const ensureSpace = (needed: number) => {
        if (y + needed > pageHeight - margin) {
          pdf.addPage();
          y = margin;
        }
      };

      const writeSectionTitle = (title: string, color: RGB = COLORS.text) => {
        ensureSpace(10);
        setTextColor(color);
        pdf.setFont('helvetica', 'bold');
        pdf.setFontSize(13);
        pdf.text(sanitizeText(title), margin, y);
        y += 6;
        setTextColor(COLORS.text);
      };

      const writeKeyValue = (key: string, value: string, indent = 0) => {
        pdf.setFont('helvetica', 'bold');
        pdf.setFontSize(10);
        const safeKey = sanitizeText(key);
        const dynamicLabelWidth = Math.ceil(pdf.getTextWidth(`${safeKey}:`)) + 8;
        const labelWidth = Math.max(36, Math.min(80, dynamicLabelWidth));
        const valueX = margin + indent + labelWidth;
        const wrapped = pdf.splitTextToSize(sanitizeText(value || '-'), contentWidth - indent - labelWidth - 2);
        const blockHeight = Math.max(5.5, wrapped.length * 4.4);

        ensureSpace(blockHeight);
        setTextColor(COLORS.text);
        pdf.text(`${safeKey}:`, margin + indent, y);

        pdf.setFont('helvetica', 'normal');
        pdf.text(wrapped, valueX, y);
        y += blockHeight + 0.8;
      };

      const writeWrapped = (text: string, indent = 0, size = 9) => {
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(size);
        const wrapped = pdf.splitTextToSize(sanitizeText(text), contentWidth - indent);
        ensureSpace((wrapped.length + 1) * 4.5);
        pdf.text(wrapped, margin + indent, y);
        y += wrapped.length * 4.5;
      };

      const writeNumberedFindings = (title: string, findings: string[], indent = 0, size = 9) => {
        pdf.setFont('helvetica', 'normal');
        pdf.setFontSize(size);
        const prefix = `${sanitizeText(title)}:`;
        const lines: string[] = [];
        findings.forEach((item, idx) => {
          const wrapped = pdf.splitTextToSize(`${idx + 1}. ${sanitizeText(item)}`, contentWidth - indent - 2);
          lines.push(...wrapped);
        });
        const full = [prefix, ...lines];
        ensureSpace((full.length + 1) * 4.5);
        pdf.text(full, margin + indent, y);
        y += full.length * 4.5;
      };

      const drawTable = (
        headers: string[],
        rows: string[][],
        colWidths: number[],
        headerFill: RGB = COLORS.tableHeaderFill,
        headerText: RGB = COLORS.tableHeaderText,
      ) => {
        const lineHeight = 4.2;
        const headerHeight = 8;
        ensureSpace(headerHeight + 10);

        let x = margin;
        pdf.setFillColor(headerFill[0], headerFill[1], headerFill[2]);
        pdf.setDrawColor(COLORS.tableBorder[0], COLORS.tableBorder[1], COLORS.tableBorder[2]);
        pdf.rect(margin, y, contentWidth, headerHeight, 'FD');

        pdf.setFont('helvetica', 'bold');
        pdf.setFontSize(9);
        setTextColor(headerText);

        headers.forEach((header, i) => {
          pdf.text(sanitizeText(header), x + 1.5, y + 5.2);
          x += colWidths[i];
          if (i < headers.length - 1) {
            pdf.line(x, y, x, y + headerHeight);
          }
        });

        y += headerHeight;
        setTextColor(COLORS.text);
        pdf.setFont('helvetica', 'normal');

        rows.forEach((row) => {
          const wrappedCells = row.map((cell, i) => pdf.splitTextToSize(sanitizeText(cell || '-'), colWidths[i] - 3));
          const maxLines = Math.max(1, ...wrappedCells.map((lines) => lines.length));
          const rowHeight = Math.max(6, maxLines * lineHeight + 2);
          ensureSpace(rowHeight);

          let cellX = margin;
          pdf.setDrawColor(COLORS.tableBorder[0], COLORS.tableBorder[1], COLORS.tableBorder[2]);
          pdf.rect(margin, y, contentWidth, rowHeight);

          wrappedCells.forEach((lines, i) => {
            pdf.text(lines, cellX + 1.5, y + 4.5);
            cellX += colWidths[i];
            if (i < wrappedCells.length - 1) {
              pdf.line(cellX, y, cellX, y + rowHeight);
            }
          });

          y += rowHeight;
        });

        y += 2;
      };

      pdf.setFont('helvetica', 'bold');
      pdf.setFontSize(22);
      setTextColor(COLORS.title);
      pdf.text('SCANNING REPORT', pageWidth / 2, 28, { align: 'center' });
      y = 40;

      writeKeyValue('URL', results.url || url);
      writeKeyValue('Scan Date', formatDate(scanStart));
      writeKeyValue('Scan Start Time', formatTime(scanStart));
      writeKeyValue('Scan End Time', formatTime(scanEnd));
      writeKeyValue('Scan Duration', formatDuration(durationSeconds));
      y += 2;

      ensureSpace(76);
      const boxX = margin;
      const boxY = y;
      const boxH = 72;

      pdf.setFillColor(COLORS.summaryBoxFill[0], COLORS.summaryBoxFill[1], COLORS.summaryBoxFill[2]);
      pdf.setDrawColor(COLORS.summaryBoxBorder[0], COLORS.summaryBoxBorder[1], COLORS.summaryBoxBorder[2]);
      pdf.roundedRect(boxX, boxY, contentWidth, boxH, 2, 2, 'FD');

      const summaryRows: Array<{ label: string; value: string; color?: RGB }> = [
        { label: 'URLs Scanned', value: String(totalUrls) },
        { label: 'Total Vulnerabilities', value: String(totalVulns) },
        { label: 'SQL Injection', value: String(sqli.length), color: COLORS.modules.sqli },
        { label: 'Cross-Site Scripting', value: String(xss.length), color: COLORS.modules.xss },
        { label: 'CSRF', value: String(csrf.length), color: COLORS.modules.csrf },
        { label: 'Overall Risk Level', value: overallRisk },
        { label: 'Server Type', value: serverType },
      ];

      let summaryY = boxY + 8;
      summaryRows.forEach((row) => {
        pdf.setFont('helvetica', 'bold');
        setTextColor(row.color || COLORS.text);
        pdf.text(sanitizeText(row.label), boxX + 4, summaryY);

        setTextColor(COLORS.title);
        pdf.text(sanitizeText(row.value), boxX + contentWidth - 4, summaryY, { align: 'right' });
        summaryY += 8.8;
      });

      setTextColor(COLORS.text);
      y = boxY + boxH + 8;

      writeSectionTitle('Executive Summary');
      writeKeyValue('Target Domain', getHostname(results.url || url));
      writeKeyValue('Total Requests Sent', `${totalRequestsSent}`);
      writeKeyValue('Total Forms Detected', `${totalFormsDetected}`);
      writeKeyValue('Total Input Parameters Tested', `${totalParamsTested}`);
      y += 2;

      const posture =
        overallRisk === 'Critical'
          ? 'Security posture is weak. Immediate remediation is required due to critical exposure.'
          : overallRisk === 'High'
            ? 'Security posture is moderate-to-weak. High-risk findings should be prioritized.'
            : overallRisk === 'Medium'
              ? 'Security posture is moderate. Hardening and validation controls should be improved.'
              : 'Security posture is relatively stable based on current scan output.';
      writeWrapped(`Security Posture: ${posture}`);

      const majorCriticalFindings =
        sqli.length > 0
          ? sqli
              .slice(0, 5)
              .map((v) => `${v.url || '-'} | ${v.parameter || v.param || '-'}`)
          : ['No critical findings reported.'];
      writeNumberedFindings('Major Critical Findings', majorCriticalFindings);
      y += 2;

      writeSectionTitle('Severity Distribution');
      drawTable(
        ['Severity', 'Count'],
        [
          ['Critical', String(severityCounts.Critical)],
          ['High', String(severityCounts.High)],
          ['Medium', String(severityCounts.Medium)],
          ['Low', String(severityCounts.Low)],
        ],
        [120, contentWidth - 120],
      );
      y += 2;

      writeSectionTitle('Detailed Vulnerability Report');

      writeSectionTitle('1. SQL INJECTION', COLORS.modules.sqli);
      writeKeyValue('Total Found', `${sqli.length}`);
      writeKeyValue('Highest Severity', getHighestSeverity(sqliSeverities));
      drawTable(
        ['ID', 'URL', 'Parameter', 'Severity'],
        sqli.map((v, i) => [
          `SQLI-${String(i + 1).padStart(3, '0')}`,
          v.url || '-',
          v.parameter || v.param || '-',
          toSeverity(v, 'Critical'),
        ]),
        [22, 92, 38, contentWidth - 152],
        [254, 226, 226],
        COLORS.modules.sqli,
      );

      sqli.forEach((v, i) => {
        ensureSpace(36);
        setTextColor(COLORS.modules.sqli);
        pdf.setFont('helvetica', 'bold');
        pdf.setFontSize(10);
        pdf.text(`Vulnerability ID: SQLI-${String(i + 1).padStart(3, '0')}`, margin, y);
        setTextColor(COLORS.text);
        y += 5;
        writeKeyValue('Affected URL', v.url || '-');
        writeKeyValue('HTTP Method', 'GET/POST');
        writeKeyValue('Vulnerable Parameter', v.parameter || v.param || '-');
        writeKeyValue('Payload Used', v.payload || '-');
        writeKeyValue('Detection Type', v.type || 'Error-based / Time-based / Boolean-based');
        writeKeyValue('Response Evidence', v.details || v.message || 'Unexpected response behavior observed.');
        writeKeyValue('Severity', toSeverity(v, 'Critical'));
        y += 1;
      });

      writeSectionTitle('2. CROSS-SITE SCRIPTING (XSS)', COLORS.modules.xss);
      writeKeyValue('Total Found', `${xss.length}`);
      writeKeyValue('Highest Severity', getHighestSeverity(xssSeverities));
      drawTable(
        ['ID', 'URL', 'Parameter', 'XSS Type', 'Severity'],
        xss.map((v, i) => [
          `XSS-${String(i + 1).padStart(3, '0')}`,
          v.url || '-',
          v.parameter || v.param || '-',
          detectXssType(v),
          toSeverity(v, 'High'),
        ]),
        [22, 70, 30, 45, contentWidth - 167],
        [255, 237, 213],
        COLORS.modules.xss,
      );

      xss.forEach((v, i) => {
        ensureSpace(36);
        setTextColor(COLORS.modules.xss);
        pdf.setFont('helvetica', 'bold');
        pdf.setFontSize(10);
        pdf.text(`Vulnerability ID: XSS-${String(i + 1).padStart(3, '0')}`, margin, y);
        setTextColor(COLORS.text);
        y += 5;
        writeKeyValue('XSS Type', detectXssType(v));
        writeKeyValue('Affected URL', v.url || '-');
        writeKeyValue('HTTP Method', 'GET/POST');
        writeKeyValue('Vulnerable Parameter', v.parameter || v.param || '-');
        writeKeyValue('Payload Used', v.payload || '-');
        writeKeyValue('Reflected Evidence', v.details || v.message || 'Payload reflected in response context.');
        writeKeyValue('Severity', toSeverity(v, 'High'));
        y += 1;
      });

      writeSectionTitle('3. CROSS-SITE REQUEST FORGERY (CSRF)', COLORS.modules.csrf);
      writeKeyValue('Total Found', `${csrf.length}`);
      writeKeyValue('Highest Severity', getHighestSeverity(csrfSeverities));
      drawTable(
        ['ID', 'Affected Form/URL', 'Issue Type', 'Severity'],
        csrf.map((v, i) => [
          `CSRF-${String(i + 1).padStart(3, '0')}`,
          `${v.formName || '-'} ${v.url ? `| ${v.url}` : ''}`,
          v.vulnerability_type || v.type || 'Missing Token / POST over HTTP / No Referer Validation',
          toSeverity(v, 'Medium'),
        ]),
        [22, 90, 58, contentWidth - 170],
        [219, 234, 254],
        COLORS.modules.csrf,
      );

      csrf.forEach((v, i) => {
        ensureSpace(34);
        setTextColor(COLORS.modules.csrf);
        pdf.setFont('helvetica', 'bold');
        pdf.setFontSize(10);
        pdf.text(`Vulnerability ID: CSRF-${String(i + 1).padStart(3, '0')}`, margin, y);
        setTextColor(COLORS.text);
        y += 5;
        writeKeyValue('Affected URL/Form', `${v.formName || '-'} ${v.url ? `| ${v.url}` : ''}`);
        writeKeyValue('HTTP Method', 'POST');
        writeKeyValue('Issue Type', v.vulnerability_type || v.type || 'Missing Token / POST over HTTP / No Referer Validation');
        writeKeyValue('Evidence', v.details || v.message || 'Anti-CSRF control validation failed.');
        writeKeyValue('Severity', toSeverity(v, 'Medium'));
        y += 1;
      });

      writeSectionTitle('Payload Testing Summary');
      writeKeyValue('Total Payloads Tested', `${totalPayloadsTested}`);
      writeKeyValue('Successful Payloads', `${successfulPayloads}`);
      writeKeyValue('Blocked Payloads', `${blockedPayloads}`);
      drawTable(
        ['Vulnerability Type', 'Payload Used', 'Status', 'Response Code'],
        payloadEntries.map((p) => [p.vulnerabilityType, p.payloadUsed, p.status, String(p.responseCode)]),
        [42, 95, 25, contentWidth - 162],
      );

      y += 2;
      writeSectionTitle('Performance Metrics');
      drawTable(
        ['Metric', 'Value'],
        [
          ['Total Requests Sent', String(totalRequestsSent)],
          ['Total Responses Received', String(totalResponsesReceived)],
          ['Average Response Time', `${averageResponseTime.toFixed(2)} ms`],
          ['Scan Mode', scanMode || '-'],
          ['Thread Count Used', String(threadCount)],
          ['Errors Encountered', String(errorsEncountered)],
        ],
        [118, contentWidth - 118],
      );

      pdf.save('report.pdf');
      onDownload?.();
    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF');
    }
  };

  return (
    <button
      onClick={handleGeneratePDF}
      className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-primary to-secondary text-white rounded-lg font-semibold hover:shadow-lg active:scale-95 transition-all"
    >
      <File className="h-5 w-5" />
      <span>{label}</span>
      <Download className="h-4 w-4" />
    </button>
  );
};
