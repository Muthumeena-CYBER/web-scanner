import React from 'react';
import { Download, FileJson, FileText, Code2, Eye } from 'lucide-react';
import { ScanResult } from '../types';
import { getRiskInfo, getTotalUrls, getVulnerabilityCounts } from '../utils/scanMetrics';
import { API_BASE } from '../services/api';

interface ReportViewerProps {
  result: ScanResult | null;
  onFormatChange?: (format: 'html' | 'json' | 'csv') => void;
}

export function ReportViewer({ result, onFormatChange }: ReportViewerProps) {
  if (!result) return null;

  const counts = getVulnerabilityCounts(result);
  const totalUrls = getTotalUrls(result);
  const riskInfo = getRiskInfo(counts);

  const groupFindingsByPayloadAndType = () => {
    const groups = new Map<string, { type: string; payload: string; entries: string[] }>();
    const allFindings = [
      ...(result.vulnerabilities?.sqli || []),
      ...(result.vulnerabilities?.xss || []),
      ...(result.vulnerabilities?.csrf || []),
    ];

    allFindings.forEach((finding) => {
      const payload = finding.payload || 'Unknown Payload';
      const type = finding.type || finding.vulnerability_type || 'Unknown Type';
      const url = finding.url || 'Unknown URL';
      const param = finding.parameter || finding.param || finding.formName || finding.component || 'Unknown Param';
      const key = `${type}::${payload}`;
      const entry = `${url} (${param})`;

      if (!groups.has(key)) {
        groups.set(key, { type, payload, entries: [] });
      }
      groups.get(key)!.entries.push(entry);
    });

    return Array.from(groups.values());
  };

  const groupedFindings = groupFindingsByPayloadAndType();

  const downloadReport = async (format: 'html' | 'json' | 'csv') => {
    try {
      const response = await fetch(`${API_BASE}/report`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: result.url,
          format,
          vulnerabilities: result.vulnerabilities,
          sitemap_urls: result.sitemap_urls || result.sitemapData?.urls,
          profile: result.profile || 'standard'
        })
      });

      if (!response.ok) throw new Error('Failed to generate report');

      const data = await response.json();

      if (format === 'json') {
        // Download JSON
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(JSON.stringify(data.report, null, 2)));
        element.setAttribute('download', data.filename);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
      } else {
        // For CSV and HTML, trigger generation on server
        console.log(`Report generated: ${data.filename}`);
      }
    } catch (err) {
      console.error('Error generating report:', err);
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 mt-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Scan Report</h2>
        <p className="text-gray-600">Download your security scan report in multiple formats</p>
      </div>

      {/* Report Format Options */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <button
          onClick={() => downloadReport('json')}
          className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all text-left group"
        >
          <div className="flex items-center gap-3 mb-2">
            <FileJson size={24} className="text-blue-600 group-hover:scale-110 transition-transform" />
            <span className="font-semibold text-gray-900">JSON Report</span>
          </div>
          <p className="text-sm text-gray-600">Complete scan data in JSON format</p>
          <div className="flex items-center gap-2 text-blue-600 text-sm mt-2">
            <Download size={16} />
            <span>Download</span>
          </div>
        </button>

        <button
          onClick={() => downloadReport('csv')}
          className="p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-all text-left group"
        >
          <div className="flex items-center gap-3 mb-2">
            <Code2 size={24} className="text-green-600 group-hover:scale-110 transition-transform" />
            <span className="font-semibold text-gray-900">CSV Report</span>
          </div>
          <p className="text-sm text-gray-600">Findings in spreadsheet format</p>
          <div className="flex items-center gap-2 text-green-600 text-sm mt-2">
            <Download size={16} />
            <span>Download</span>
          </div>
        </button>

        <button
          onClick={() => downloadReport('html')}
          className="p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-all text-left group"
        >
          <div className="flex items-center gap-3 mb-2">
            <FileText size={24} className="text-purple-600 group-hover:scale-110 transition-transform" />
            <span className="font-semibold text-gray-900">HTML Report</span>
          </div>
          <p className="text-sm text-gray-600">Professional HTML report</p>
          <div className="flex items-center gap-2 text-purple-600 text-sm mt-2">
            <Download size={16} />
            <span>Download</span>
          </div>
        </button>
      </div>

      {/* Executive Summary */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <Eye size={20} /> Executive Summary
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <div className="text-3xl font-bold text-red-600">
              {counts.sqli}
            </div>
            <div className="text-sm text-gray-600">Critical (SQLi)</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-orange-600">
              {counts.xss}
            </div>
            <div className="text-sm text-gray-600">High (XSS)</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-yellow-600">
              {counts.csrf}
            </div>
            <div className="text-sm text-gray-600">Medium (CSRF)</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-blue-600">
              {totalUrls}
            </div>
            <div className="text-sm text-gray-600">URLs Scanned</div>
          </div>
        </div>
      </div>

      {/* Risk Assessment */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="font-semibold text-gray-900 mb-3">Risk Assessment</h3>
        <p className="text-sm text-gray-700 mb-3">
          Overall Risk Level:{' '}
          <span className={`font-bold ${riskInfo.text}`}>{riskInfo.level}</span>
        </p>
        <ul className="text-sm text-gray-700 space-y-1">
          <li>Scan Coverage: {totalUrls} URLs</li>
          <li>Modules Enabled: SQLi, XSS, CSRF</li>
          <li>Report Generated: {new Date(result.timestamp).toLocaleString()}</li>
        </ul>
      </div>

      {groupedFindings.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4 mt-6">
          <h3 className="font-semibold text-gray-900 mb-3">Grouped Payloads</h3>
          <div className="space-y-4">
            {groupedFindings.map((group, idx) => (
              <div key={`${group.type}-${idx}`} className="border border-gray-200 rounded-lg bg-white p-4">
                <div className="text-sm text-gray-700 mb-2">
                  <span className="font-semibold text-gray-900">{group.type}</span>
                </div>
                <div className="text-sm text-gray-700 mb-3">
                  <span className="font-medium">Payload:</span>{' '}
                  <code className="bg-gray-100 px-2 py-1 rounded text-xs">{group.payload}</code>
                </div>
                <div className="space-y-1 text-sm text-gray-700">
                  {group.entries.map((entry, entryIdx) => (
                    <div key={`${group.type}-${idx}-${entryIdx}`}>{entry}</div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
