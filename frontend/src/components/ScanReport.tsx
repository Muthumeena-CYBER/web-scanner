import React from 'react';
import { ScanResult } from '../types';
import { SitemapDisplay } from './SitemapDisplay';

interface ScanReportProps {
  result: ScanResult;
}

const getOverallRisk = (sqliCount: number, xssCount: number, csrfCount: number): string => {
  if (sqliCount > 0) return 'Critical';
  if (xssCount > 0) return 'High';
  if (csrfCount > 0) return 'Medium';
  return 'Low';
};

export const ScanReport: React.FC<ScanReportProps> = ({ result }) => {
  const sqliCount = result.vulnerabilities.sqli?.length || 0;
  const xssCount = result.vulnerabilities.xss?.length || 0;
  const csrfCount = result.vulnerabilities.csrf?.length || 0;
  const totalVulns = sqliCount + xssCount + csrfCount;

  const totalUrls = result.sitemapData?.totalUrls ?? result.sitemap_urls?.length ?? 0;
  const sitemapImage = result.sitemapData?.sitemapImage;
  const overallRisk = getOverallRisk(sqliCount, xssCount, csrfCount);
  const serverType = result.server?.type || 'Unknown';

  const summaryRows = [
    { label: 'URLs Scanned', value: String(totalUrls), color: 'text-slate-800' },
    { label: 'Total Vulnerabilities', value: String(totalVulns), color: 'text-slate-800' },
    { label: 'SQL Injection', value: String(sqliCount), color: 'text-red-700' },
    { label: 'Cross-Site Scripting', value: String(xssCount), color: 'text-orange-700' },
    { label: 'CSRF', value: String(csrfCount), color: 'text-blue-700' },
    { label: 'Overall Risk Level', value: overallRisk, color: 'text-slate-800' },
    { label: 'Server Type', value: serverType, color: 'text-slate-800' },
  ];

  return (
    <div className="w-full bg-white space-y-8">
      <div className="text-sm text-gray-600">
        Report for <span className="font-semibold text-gray-900">{result.url}</span> -{' '}
        {new Date(result.timestamp).toLocaleString()}
      </div>

      <div className="rounded-xl border border-sky-700 bg-sky-100 p-6">
        <div className="space-y-5">
          {summaryRows.map((row) => (
            <div key={row.label} className="grid grid-cols-[1fr_auto] items-center gap-6">
              <span className={`text-lg sm:text-2xl md:text-3xl font-semibold leading-tight ${row.color}`}>
                {row.label}
              </span>
              <span className="text-lg sm:text-2xl md:text-3xl font-bold text-slate-900 leading-tight">
                {row.value}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
        Vulnerability finding details are available in the generated PDF report only.
      </div>

      {(sitemapImage || totalUrls > 0) && <SitemapDisplay sitemapImage={sitemapImage} totalUrls={totalUrls} />}
    </div>
  );
};
