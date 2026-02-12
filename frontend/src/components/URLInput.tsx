import React, { useState } from 'react';
import { Search, AlertCircle } from 'lucide-react';

interface URLInputProps {
  onScan: (url: string) => void;
  isLoading: boolean;
  value?: string;
  onUrlChange?: (url: string) => void;
}

export const URLInput: React.FC<URLInputProps> = ({ onScan, isLoading, value, onUrlChange }) => {
  const [internalUrl, setInternalUrl] = useState<string>('');
  const [error, setError] = useState<string>('');
  const url = value !== undefined ? value : internalUrl;

  const validateUrl = (urlString: string): boolean => {
    try {
      const urlObj = new URL(urlString);
      return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
      return false;
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!url.trim()) {
      setError('Please enter a URL');
      return;
    }

    if (!validateUrl(url)) {
      setError('Please enter a valid URL (e.g., https://example.com)');
      return;
    }

    onScan(url);
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Target URL
          </label>
          <div className="relative">
            <Search className="absolute left-4 top-3.5 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={url}
              onChange={(e) => {
      if (onUrlChange) {
        onUrlChange(e.target.value);
      } else {
        setInternalUrl(e.target.value);
      }
      setError('');
    }}
              placeholder="https://example.com"
              className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary transition-colors"
              disabled={isLoading}
            />
          </div>
          {error && (
            <div className="mt-2 flex items-center gap-2 text-danger">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">{error}</span>
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className={`w-full py-3 px-6 rounded-lg font-semibold transition-all duration-200 flex items-center justify-center gap-2 ${
            isLoading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-primary hover:bg-primary/90 text-white hover:shadow-lg active:scale-95'
          }`}
        >
          {isLoading ? (
            <>
              <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
              Scanning...
            </>
          ) : (
            <>
              <Search className="h-5 w-5" />
              Start Scan
            </>
          )}
        </button>
      </form>
    </div>
  );
};
