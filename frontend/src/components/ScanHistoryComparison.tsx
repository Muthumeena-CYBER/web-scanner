import React, { useState, useEffect } from 'react';
import { TrendingDown, TrendingUp, Calendar } from 'lucide-react';
import { API_BASE } from '../services/api';

interface ScanHistoryComparison {
  url: string;
  history: any[];
  currentIndex: number;
}

interface ScanHistoryProps {
  url: string | null;
  onSelectScan?: (scan: any) => void;
}

export function ScanHistoryComparison({ url, onSelectScan }: ScanHistoryProps) {
  const [history, setHistory] = useState<any[]>([]);
  const [comparison, setComparison] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedScan1, setSelectedScan1] = useState<number | null>(null);
  const [selectedScan2, setSelectedScan2] = useState<number | null>(null);

  useEffect(() => {
    if (url) {
      fetchHistory();
    }
  }, [url]);

  const fetchHistory = async () => {
    if (!url) return;
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/history?url=${encodeURIComponent(url)}`);
      const data = await response.json();
      if (data.success && data.history) {
        setHistory(data.history);
        if (data.history.length >= 2) {
          setSelectedScan1(data.history.length - 2);
          setSelectedScan2(data.history.length - 1);
        }
      }
    } catch (err) {
      console.error('Error fetching history:', err);
    } finally {
      setLoading(false);
    }
  };

  const compareScans = async () => {
    if (!url || selectedScan1 === null || selectedScan2 === null) return;
    setLoading(true);
    try {
      const response = await fetch(
        `${API_BASE}/compare?url=${encodeURIComponent(url)}&scan1=${selectedScan1}&scan2=${selectedScan2}`
      );
      const data = await response.json();
      if (data.success) {
        setComparison(data.comparison);
      }
    } catch (err) {
      console.error('Error comparing scans:', err);
    } finally {
      setLoading(false);
    }
  };

  if (!url || history.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6 mt-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Scan History and Regression Tracking</h2>
        <p className="text-gray-600">No scan history available. Run multiple scans to compare results.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 mt-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Scan History and Regression Tracking</h2>

      {/* Scan Selection */}
      <div className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Previous Scan</label>
            <select
              value={selectedScan1 ?? ''}
              onChange={(e) => setSelectedScan1(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {history.map((scan, idx) => (
                <option key={idx} value={idx}>
                  {new Date(scan.timestamp).toLocaleDateString()} {new Date(scan.timestamp).toLocaleTimeString()}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end justify-center">
            <button
              onClick={compareScans}
              disabled={loading || selectedScan1 === null || selectedScan2 === null}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-medium"
            >
              {loading ? 'Comparing...' : 'Compare'}
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Current Scan</label>
            <select
              value={selectedScan2 ?? ''}
              onChange={(e) => setSelectedScan2(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {history.map((scan, idx) => (
                <option key={idx} value={idx}>
                  {new Date(scan.timestamp).toLocaleDateString()} {new Date(scan.timestamp).toLocaleTimeString()}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Calendar size={20} /> Scan Timeline
        </h3>
        <div className="space-y-2">
          {history.map((scan, idx) => (
            <div
              key={idx}
              className={`p-3 rounded-lg border ${
                idx === selectedScan1 || idx === selectedScan2
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              } cursor-pointer transition-colors`}
              onClick={() => {
                if (idx === selectedScan1) {
                  setSelectedScan1(idx);
                } else {
                  setSelectedScan2(idx);
                }
              }}
            >
              <div className="flex flex-wrap justify-between items-center gap-2">
                <div>
                  <div className="font-medium text-gray-900">
                    {new Date(scan.timestamp).toLocaleDateString()} {new Date(scan.timestamp).toLocaleTimeString()}
                  </div>
                  <div className="text-sm text-gray-600">
                    SQLi: {scan.summary.sqli} | XSS: {scan.summary.xss} | CSRF: {scan.summary.csrf}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {idx === selectedScan1 && (
                    <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Previous</span>
                  )}
                  {idx === selectedScan2 && (
                    <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">Current</span>
                  )}
                  {onSelectScan && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectScan(scan);
                      }}
                      className="text-xs bg-gray-900 text-white px-2 py-1 rounded hover:bg-gray-800"
                    >
                      View Report
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Comparison Results */}
      {comparison && (
        <div className="border-t pt-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Regression Analysis</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Improvements */}
            <div className="bg-green-50 rounded-lg p-4 border border-green-200">
              <div className="flex items-center gap-2 mb-3">
                <TrendingDown size={20} className="text-green-600" />
                <h4 className="font-semibold text-green-900">Fixed Vulnerabilities</h4>
              </div>
              {Object.values(comparison.improvements).flat().length > 0 ? (
                <div className="space-y-2">
                  {Object.entries(comparison.improvements).map(([type, vulns]: any) =>
                    vulns.length > 0 && (
                      <div key={type}>
                        <div className="text-sm font-medium text-green-800 capitalize">{type}</div>
                        <div className="text-2xl font-bold text-green-600">{vulns.length}</div>
                      </div>
                    )
                  )}
                </div>
              ) : (
                <p className="text-green-700 text-sm">No vulnerabilities fixed</p>
              )}
            </div>

            {/* Regressions */}
            <div className="bg-red-50 rounded-lg p-4 border border-red-200">
              <div className="flex items-center gap-2 mb-3">
                <TrendingUp size={20} className="text-red-600" />
                <h4 className="font-semibold text-red-900">New Vulnerabilities</h4>
              </div>
              {Object.values(comparison.regressions).flat().length > 0 ? (
                <div className="space-y-2">
                  {Object.entries(comparison.regressions).map(([type, vulns]: any) =>
                    vulns.length > 0 && (
                      <div key={type}>
                        <div className="text-sm font-medium text-red-800 capitalize">{type}</div>
                        <div className="text-2xl font-bold text-red-600">{vulns.length}</div>
                      </div>
                    )
                  )}
                </div>
              ) : (
                <p className="text-red-700 text-sm">No new vulnerabilities detected</p>
              )}
            </div>
          </div>

          {/* Overall Recommendation */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-900">
              <span className="font-semibold">Recommendation:</span>{' '}
              {Object.values(comparison.improvements).flat().length > 0
                ? 'Great progress! Keep working on the remaining issues.'
                : Object.values(comparison.regressions).flat().length > 0
                ? 'Caution: New vulnerabilities detected. Immediate action required.'
                : 'No changes detected. Continue regular security audits.'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
