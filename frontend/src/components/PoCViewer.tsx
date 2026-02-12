import React, { useState } from 'react';
import { ChevronDown, Copy, Check } from 'lucide-react';
import { ScanResult } from '../types';

interface PoCViewerProps {
  result: ScanResult | null;
}

export function PoCViewer({ result }: PoCViewerProps) {
  const [expandedPoCs, setExpandedPoCs] = useState<Set<string>>(new Set());
  const [copiedPoC, setCopiedPoC] = useState<string | null>(null);

  if (!result) return null;

  const togglePoC = (pocId: string) => {
    const newExpanded = new Set(expandedPoCs);
    if (newExpanded.has(pocId)) {
      newExpanded.delete(pocId);
    } else {
      newExpanded.add(pocId);
    }
    setExpandedPoCs(newExpanded);
  };

  const copyToClipboard = (text: string, pocId: string) => {
    navigator.clipboard.writeText(text);
    setCopiedPoC(pocId);
    setTimeout(() => setCopiedPoC(null), 2000);
  };

  const renderPoCSection = (title: string, findings: any[], type: 'sqli' | 'xss' | 'csrf') => {
    if (!findings || findings.length === 0) return null;

    return (
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          {type === 'sqli' && 'SQL Injection'}
          {type === 'xss' && 'Cross-Site Scripting'}
          {type === 'csrf' && 'CSRF Vulnerabilities'}
          <span className="text-sm font-normal bg-gray-100 px-2 py-1 rounded">
            {findings.length}
          </span>
        </h3>

        <div className="space-y-2">
          {findings.map((finding, idx) => {
            const pocId = `${type}-${idx}`;
            const isExpanded = expandedPoCs.has(pocId);
            const hasRequest = (finding.parameter || finding.param) && finding.payload;

            return (
              <div
                key={pocId}
                className={`border rounded-lg overflow-hidden transition-all ${
                  type === 'sqli' ? 'border-red-200' :
                  type === 'xss' ? 'border-orange-200' :
                  'border-yellow-200'
                }`}
              >
                <button
                  onClick={() => togglePoC(pocId)}
                  className={`w-full px-4 py-3 flex items-center justify-between ${
                    type === 'sqli' ? 'bg-red-50 hover:bg-red-100' :
                    type === 'xss' ? 'bg-orange-50 hover:bg-orange-100' :
                    'bg-yellow-50 hover:bg-yellow-100'
                  } transition-colors`}
                >
                  <div className="text-left">
                    <div className={`font-medium ${
                      type === 'sqli' ? 'text-red-900' :
                      type === 'xss' ? 'text-orange-900' :
                      'text-yellow-900'
                    }`}>
                      {(finding.parameter || finding.param || finding.formName || finding.component || 'Form/Component')} - {finding.type || 'Unknown'}
                    </div>
                    <div className="text-xs text-gray-600 mt-1">{finding.url}</div>
                  </div>
                  <ChevronDown
                    size={20}
                    className={`transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                  />
                </button>

                {isExpanded && (
                  <div className="px-4 py-4 bg-white border-t border-gray-200 space-y-4">
                    {hasRequest && (
                      <>
                        {/* Request */}
                        <div>
                        <div className="text-sm font-semibold text-gray-700 mb-2">Request</div>
                          <div className="relative bg-gray-900 text-gray-100 p-3 rounded font-mono text-xs overflow-x-auto">
                            <pre>{`GET ${finding.url}?${finding.parameter || finding.param}=${finding.payload} HTTP/1.1`}</pre>
                            <button
                              onClick={() => copyToClipboard(
                                `GET ${finding.url}?${finding.parameter || finding.param}=${finding.payload} HTTP/1.1`,
                                `request-${pocId}`
                              )}
                              className="absolute top-2 right-2 p-2 bg-gray-800 hover:bg-gray-700 rounded"
                            >
                              {copiedPoC === `request-${pocId}` ? (
                                <Check size={16} className="text-green-500" />
                              ) : (
                                <Copy size={16} className="text-gray-400" />
                              )}
                            </button>
                          </div>
                        </div>

                        {/* Payload */}
                        <div>
                        <div className="text-sm font-semibold text-gray-700 mb-2">Payload</div>
                          <div className="relative bg-gray-900 text-gray-100 p-3 rounded font-mono text-xs overflow-x-auto">
                            <pre>{finding.payload}</pre>
                            <button
                              onClick={() => copyToClipboard(finding.payload, `payload-${pocId}`)}
                              className="absolute top-2 right-2 p-2 bg-gray-800 hover:bg-gray-700 rounded"
                            >
                              {copiedPoC === `payload-${pocId}` ? (
                                <Check size={16} className="text-green-500" />
                              ) : (
                                <Copy size={16} className="text-gray-400" />
                              )}
                            </button>
                          </div>
                        </div>
                      </>
                    )}

                    {/* Response Snippet */}
                    <div>
                      <div className="text-sm font-semibold text-gray-700 mb-2">Detection Method</div>
                      <div className="bg-gray-50 p-3 rounded text-sm text-gray-700">
                        {finding.type === 'Error-based SQLi' && (
                          'Detected via SQL error messages in response'
                        )}
                        {finding.type === 'Boolean-based SQLi' && (
                          'Detected via comparison of true/false payloads'
                        )}
                        {finding.type === 'Time-based SQLi' && (
                          'Detected via response time delays'
                        )}
                        {finding.type === 'Reflected XSS' && (
                          'Payload reflected in HTML response without encoding'
                        )}
                        {finding.type === 'CSRF Detection' && (
                          'Form detected without CSRF token protection'
                        )}
                      </div>
                    </div>

                    {/* Risk Assessment */}
                    <div>
                      <div className="text-sm font-semibold text-gray-700 mb-2">Risk Level</div>
                      <div className={`inline-block px-3 py-1 rounded text-sm font-semibold ${
                        type === 'sqli' ? 'bg-red-100 text-red-800' :
                        type === 'xss' ? 'bg-orange-100 text-orange-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {type === 'sqli' ? 'CRITICAL' : type === 'xss' ? 'HIGH' : 'MEDIUM'}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 mt-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-2">Proof of Concepts</h2>
      <p className="text-gray-600 mb-6">
        Detailed vulnerability information with requests and payloads
      </p>

      {renderPoCSection('SQL Injection', result.vulnerabilities?.sqli, 'sqli')}
      {renderPoCSection('Cross-Site Scripting', result.vulnerabilities?.xss, 'xss')}
      {renderPoCSection('CSRF', result.vulnerabilities?.csrf, 'csrf')}

      {!result.vulnerabilities?.sqli?.length &&
       !result.vulnerabilities?.xss?.length &&
       !result.vulnerabilities?.csrf?.length && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
          <p className="text-green-800 font-semibold">No vulnerabilities found.</p>
          <p className="text-green-700 text-sm mt-2">
            All scanned URLs passed the security checks.
          </p>
        </div>
      )}
    </div>
  );
}
