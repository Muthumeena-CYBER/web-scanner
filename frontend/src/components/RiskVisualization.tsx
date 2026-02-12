import React from 'react';
import { ScanResult } from '../types';
import { getRiskInfo, getVulnerabilityCounts } from '../utils/scanMetrics';
import { BarChart, PieChart } from 'lucide-react';

interface RiskVisualizationProps {
  result: ScanResult | null;
}

export function RiskVisualization({ result }: RiskVisualizationProps) {
  if (!result) return null;

  const counts = getVulnerabilityCounts(result);
  const sqliCount = counts.sqli;
  const xssCount = counts.xss;
  const csrfCount = counts.csrf;
  const totalVulns = counts.total;

  // Calculate percentages
  const sqliPercent = totalVulns > 0 ? Math.round((sqliCount / totalVulns) * 100) : 0;
  const xssPercent = totalVulns > 0 ? Math.round((xssCount / totalVulns) * 100) : 0;
  const csrfPercent = totalVulns > 0 ? Math.round((csrfCount / totalVulns) * 100) : 0;

  const riskInfo = getRiskInfo(counts);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 mt-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Risk Overview</h2>

      {/* Overall Risk Score */}
      <div className={`${riskInfo.bg} rounded-lg p-6 mb-6 border-l-4 ${riskInfo.border}`}>
        <div className="text-center">
          <div className={`text-5xl font-bold ${riskInfo.text} mb-2`}>
            {riskInfo.level}
          </div>
          <p className="text-gray-700">
            {totalVulns === 0
              ? 'No vulnerabilities detected'
              : `${totalVulns} vulnerability/vulnerabilities found`}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart (represented with CSS) */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <PieChart size={20} /> Vulnerability Distribution
          </h3>

          {totalVulns > 0 ? (
            <div className="space-y-3">
              {sqliCount > 0 && (
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">SQL Injection</span>
                    <span className="text-sm font-bold text-red-600">{sqliCount} ({sqliPercent}%)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-red-600 h-3 rounded-full transition-all"
                      style={{ width: `${sqliPercent}%` }}
                    />
                  </div>
                </div>
              )}

              {xssCount > 0 && (
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">XSS</span>
                    <span className="text-sm font-bold text-orange-600">{xssCount} ({xssPercent}%)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-orange-600 h-3 rounded-full transition-all"
                      style={{ width: `${xssPercent}%` }}
                    />
                  </div>
                </div>
              )}

              {csrfCount > 0 && (
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">CSRF</span>
                    <span className="text-sm font-bold text-yellow-600">{csrfCount} ({csrfPercent}%)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-yellow-600 h-3 rounded-full transition-all"
                      style={{ width: `${csrfPercent}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              No vulnerabilities to display
            </div>
          )}
        </div>

        {/* Bar Chart */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <BarChart size={20} /> Vulnerability Count
          </h3>

          <div className="space-y-4">
            {/* SQLi Bar */}
            <div className="flex items-end gap-3 h-40">
              <div className="text-sm font-medium text-gray-700 w-20">SQL Injection</div>
              <div className="flex-1 bg-red-100 rounded-t relative" style={{ height: Math.max(sqliCount * 20, 20) + 'px' }}>
                <div className="absolute -top-6 left-0 right-0 text-center">
                  <span className="text-lg font-bold text-red-600">{sqliCount}</span>
                </div>
              </div>
            </div>

            {/* XSS Bar */}
            <div className="flex items-end gap-3 h-40">
              <div className="text-sm font-medium text-gray-700 w-20">XSS</div>
              <div className="flex-1 bg-orange-100 rounded-t relative" style={{ height: Math.max(xssCount * 20, 20) + 'px' }}>
                <div className="absolute -top-6 left-0 right-0 text-center">
                  <span className="text-lg font-bold text-orange-600">{xssCount}</span>
                </div>
              </div>
            </div>

            {/* CSRF Bar */}
            <div className="flex items-end gap-3 h-40">
              <div className="text-sm font-medium text-gray-700 w-20">CSRF</div>
              <div className="flex-1 bg-yellow-100 rounded-t relative" style={{ height: Math.max(csrfCount * 20, 20) + 'px' }}>
                <div className="absolute -top-6 left-0 right-0 text-center">
                  <span className="text-lg font-bold text-yellow-600">{csrfCount}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Vulnerability Breakdown Table */}
      <div className="mt-6 border-t pt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Detailed Breakdown</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-4 font-semibold text-gray-700">Vulnerability Type</th>
                <th className="text-right py-2 px-4 font-semibold text-gray-700">Count</th>
                <th className="text-right py-2 px-4 font-semibold text-gray-700">Percentage</th>
                <th className="text-right py-2 px-4 font-semibold text-gray-700">Severity</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-3 px-4 text-gray-700">SQL Injection</td>
                <td className="text-right py-3 px-4 font-bold text-red-600">{sqliCount}</td>
                <td className="text-right py-3 px-4 text-gray-600">{sqliPercent}%</td>
                <td className="text-right py-3 px-4">
                  <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-semibold">
                    CRITICAL
                  </span>
                </td>
              </tr>
              <tr className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-3 px-4 text-gray-700">Cross-Site Scripting</td>
                <td className="text-right py-3 px-4 font-bold text-orange-600">{xssCount}</td>
                <td className="text-right py-3 px-4 text-gray-600">{xssPercent}%</td>
                <td className="text-right py-3 px-4">
                  <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded text-xs font-semibold">
                    HIGH
                  </span>
                </td>
              </tr>
              <tr className="hover:bg-gray-50">
                <td className="py-3 px-4 text-gray-700">CSRF</td>
                <td className="text-right py-3 px-4 font-bold text-yellow-600">{csrfCount}</td>
                <td className="text-right py-3 px-4 text-gray-600">{csrfPercent}%</td>
                <td className="text-right py-3 px-4">
                  <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-xs font-semibold">
                    MEDIUM
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
