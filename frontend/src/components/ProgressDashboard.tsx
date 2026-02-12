import React from 'react';
import { CheckCircle, AlertCircle, Clock, Ban } from 'lucide-react';

interface ProgressUpdate {
  status: 'scanning' | 'completed' | 'error' | 'canceled' | 'queued';
  currentUrl?: number;
  totalUrls?: number;
  message?: string;
  findings?: {
    sqli: number;
    xss: number;
    csrf: number;
  };
}

interface ProgressDashboardProps {
  progress: ProgressUpdate | null;
  isActive: boolean;
  onCancel?: () => void;
}

export function ProgressDashboard({ progress, isActive, onCancel }: ProgressDashboardProps) {
  if (!progress) return null;

  const percentage = progress.totalUrls
    ? Math.round((progress.currentUrl || 0) / progress.totalUrls * 100)
    : 0;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
      <div className="flex items-center gap-3 mb-4">
        {(progress.status === 'scanning' || progress.status === 'queued') && (
          <>
            <div className="animate-spin">
              <Clock size={24} className="text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              {progress.status === 'queued' ? 'Scan queued...' : 'Scanning in progress...'}
            </h3>
          </>
        )}
        {progress.status === 'completed' && (
          <>
            <CheckCircle size={24} className="text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900">Scan completed!</h3>
          </>
        )}
        {progress.status === 'error' && (
          <>
            <AlertCircle size={24} className="text-red-600" />
            <h3 className="text-lg font-semibold text-gray-900">Scan error</h3>
          </>
        )}
        {progress.status === 'canceled' && (
          <>
            <Ban size={24} className="text-gray-600" />
            <h3 className="text-lg font-semibold text-gray-900">Scan canceled</h3>
          </>
        )}
      </div>

      {(progress.status === 'scanning' || progress.status === 'queued') && (
        <>
          {/* Progress bar */}
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">
                Scanning URLs: {progress.currentUrl || 0}/{progress.totalUrls || '...'}
              </span>
              <span className="text-sm font-semibold text-gray-900">{percentage}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${percentage}%` }}
              />
            </div>
          </div>

          {/* Live findings */}
          {progress.findings && (
            <div className="grid grid-cols-3 gap-3">
              <div className="p-3 bg-red-50 rounded-lg border border-red-200">
                <div className="text-2xl font-bold text-red-600">{progress.findings.sqli}</div>
                <div className="text-xs text-red-700">SQL Injection</div>
              </div>
              <div className="p-3 bg-orange-50 rounded-lg border border-orange-200">
                <div className="text-2xl font-bold text-orange-600">{progress.findings.xss}</div>
                <div className="text-xs text-orange-700">XSS Found</div>
              </div>
              <div className="p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="text-2xl font-bold text-yellow-600">{progress.findings.csrf}</div>
                <div className="text-xs text-yellow-700">CSRF Issues</div>
              </div>
            </div>
          )}

          {progress.message && (
            <p className="text-sm text-gray-600 mt-4">{progress.message}</p>
          )}

          {isActive && onCancel && (
            <div className="mt-5">
              <button
                onClick={onCancel}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors text-sm font-medium"
              >
                End Scan
              </button>
            </div>
          )}
        </>
      )}

      {progress.status === 'error' && progress.message && (
        <p className="text-sm text-red-600">{progress.message}</p>
      )}
      {progress.status === 'canceled' && progress.message && (
        <p className="text-sm text-gray-600">{progress.message}</p>
      )}
    </div>
  );
}
