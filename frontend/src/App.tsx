import { useEffect, useRef, useState } from 'react';
import { Shield, AlertCircle } from 'lucide-react';
import { URLInput } from './components/URLInput';
import { ScanReport } from './components/ScanReport';
import { PDFGenerator } from './components/PDFGenerator';
import { AdvancedConfig } from './components/AdvancedConfig';
import { ProgressDashboard } from './components/ProgressDashboard';
import { ScanHistoryComparison } from './components/ScanHistoryComparison';
import { scannerAPI } from './services/api';
import { ScanResult } from './types';
import './index.css';

type ProfileName = 'quick' | 'standard' | 'full' | 'aggressive' | 'custom';

type ProgressStatus = 'scanning' | 'completed' | 'error' | 'canceled' | 'queued';

interface ScanConfig {
  profile: ProfileName;
  maxUrls: number;
  depthLimit: number;
  timeout: number;
  verbose: boolean;
  modules: {
    sqli: boolean;
    xss: boolean;
    csrf: boolean;
  };
}

interface ProgressUpdate {
  status: ProgressStatus;
  phase?: 'web_scan' | 'port_scan' | 'finalizing' | string;
  currentUrl?: number;
  totalUrls?: number;
  currentPort?: number;
  totalPorts?: number;
  message?: string;
  findings?: {
    sqli: number;
    xss: number;
    csrf: number;
  };
}

const defaultConfig: ScanConfig = {
  profile: 'standard',
  maxUrls: 50,
  depthLimit: 2,
  timeout: 10,
  verbose: false,
  modules: { sqli: true, xss: true, csrf: true },
};

function App() {
  const [scanConfig, setScanConfig] = useState<ScanConfig>(defaultConfig);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [historyReport, setHistoryReport] = useState<ScanResult | null>(null);
  const [targetUrl, setTargetUrl] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [scanId, setScanId] = useState<string | null>(null);
  const pollRef = useRef<number | null>(null);

  const handleConfigChange = (cfg: Partial<ScanConfig>) => {
    setScanConfig((prev) => ({
      ...prev,
      ...cfg,
      maxUrls: cfg.maxUrls ?? prev.maxUrls,
      depthLimit: cfg.depthLimit ?? prev.depthLimit,
      modules: cfg.modules ?? prev.modules,
    }));
  };

  const stopPolling = () => {
    if (pollRef.current) {
      window.clearInterval(pollRef.current);
      pollRef.current = null;
    }
  };

  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, []);

  const handleScan = async (url: string) => {
    const authorizationConfirmed = window.confirm(
      'Unauthorized port scanning is illegal. Confirm you are authorized to scan this target.'
    );

    setLoading(true);
    setError(null);
    setResult(null);
    setHistoryReport(null);
    setProgress({ status: 'scanning', currentUrl: 0, totalUrls: scanConfig.maxUrls, findings: { sqli: 0, xss: 0, csrf: 0 } });

    try {
      const start = await scannerAPI.scanAsync({
        url,
        checkSQLi: scanConfig.modules.sqli,
        checkXSS: scanConfig.modules.xss,
        checkCSRF: scanConfig.modules.csrf,
        authorizationConfirmed,
        profile: scanConfig.profile,
        customConfig: {
          maxUrls: scanConfig.maxUrls,
          depthLimit: scanConfig.depthLimit,
          timeout: scanConfig.timeout,
          verbose: scanConfig.verbose,
          modules: scanConfig.modules,
        },
      });

      const newScanId = start.scan_id;
      setScanId(newScanId);

      stopPolling();
      pollRef.current = window.setInterval(async () => {
        try {
          const status = await scannerAPI.getScanStatus(newScanId);
          setProgress({
            status: status.status,
            phase: status.phase,
            currentUrl: status.currentUrl,
            totalUrls: status.totalUrls,
            currentPort: status.currentPort,
            totalPorts: status.totalPorts,
            message: status.message,
            findings: status.findings,
          });

          if (status.status === 'completed') {
            setResult(status.result);
            setLoading(false);
            setScanId(null);
            stopPolling();
          }

          if (status.status === 'error' || status.status === 'canceled') {
            setError(status.message || 'Scan failed');
            setLoading(false);
            setScanId(null);
            stopPolling();
          }
        } catch (pollError: any) {
          setError(pollError?.message || 'Failed to fetch scan status');
          setLoading(false);
          stopPolling();
        }
      }, 1000);
    } catch (err: any) {
      const message = err?.message || 'Scan failed';
      setError(message);
      setProgress({ status: 'error', message });
      setLoading(false);
    }
  };

  const handleStopScan = async () => {
    if (!scanId) return;
    try {
      await scannerAPI.stopScan(scanId);
      setProgress({ status: 'canceled', message: 'Scan canceled by user' });
      setLoading(false);
      setScanId(null);
      stopPolling();
    } catch (err: any) {
      setError(err?.message || 'Failed to stop scan');
    }
  };
  const activeReport = result || historyReport;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-white/10 rounded-full">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Web Security Scanner</h1>
              <p className="text-xs text-blue-100">Advanced Vulnerability Detection & Reporting v2.0</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
            <div className="p-8 space-y-6">
              <URLInput
                onScan={handleScan}
                isLoading={loading}
                value={targetUrl}
                onUrlChange={(value) => setTargetUrl(value)}
              />

              <div className="border-t border-gray-200 pt-6 space-y-6">
                <AdvancedConfig
                  config={scanConfig}
                  onConfigChange={handleConfigChange}
                  isOpen={advancedOpen}
                  onToggle={() => setAdvancedOpen(!advancedOpen)}
                />
              </div>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-6 rounded-lg flex gap-4">
              <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-900">Scan Error</h3>
                <p className="text-red-800 text-sm mt-1">{error}</p>
              </div>
            </div>
          )}

          <ProgressDashboard progress={progress} isActive={loading} onCancel={handleStopScan} />

          <ScanHistoryComparison
            url={targetUrl || result?.url || historyReport?.url || null}
            onSelectScan={(scan) => setHistoryReport(scan)}
          />

          {activeReport && (
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden" id="detail-report">
                <div className="p-8">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Detailed Vulnerability Report</h2>
                  <ScanReport result={activeReport} />
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4 justify-end">
                <PDFGenerator url={activeReport.url} results={activeReport} label="Download Final Report (PDF)" />
              </div>
            </div>
          )}

          {!result && !loading && !error && (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <Shield className="h-16 w-16 mx-auto opacity-40" />
              </div>
              <h2 className="text-xl font-semibold text-gray-600 mb-2">Ready to Scan</h2>
              <p className="text-gray-500 mb-4">Enter a target URL and configure your scan preferences</p>
            </div>
          )}
        </div>
      </main>

      <footer className="border-t border-gray-200 bg-gray-50 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center text-sm text-gray-600">
          <p>Web Security Scanner v2.0 | Advanced Vulnerability Detection & Reporting</p>
          <p className="mt-2 text-xs">Features: Multiple Scan Profiles, Custom Payloads, Real-time Progress, Multi-format Reports, Regression Tracking</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
