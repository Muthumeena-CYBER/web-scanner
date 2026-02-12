import React from 'react';
import { ScanResult } from '../types';
import { getRiskLevel, getTotalUrls, getVulnerabilityCounts } from '../utils/scanMetrics';

interface BriefReportProps {
  result: ScanResult;
}

export const BriefReport: React.FC<BriefReportProps> = ({ result }) => {
  const counts = getVulnerabilityCounts(result);
  const totalUrls = getTotalUrls(result);
  const totalVulns = counts.total;
  const risk = getRiskLevel(counts);

  return (
    <div className="w-full bg-white space-y-4">
      <div className="text-sm text-gray-600">
        Summary for <span className="font-semibold text-gray-900">{result.url}</span>
      </div>

      <ul className="space-y-2 text-sm text-gray-800 list-disc pl-5">
        <li>Overall risk: {risk}</li>
        <li>Total vulnerabilities: {totalVulns}</li>
        <li>SQL Injection: {counts.sqli} | XSS: {counts.xss} | CSRF: {counts.csrf}</li>
        <li>URLs scanned: {totalUrls}</li>
        <li>Scan time: {new Date(result.timestamp).toLocaleString()}</li>
      </ul>
    </div>
  );
};
