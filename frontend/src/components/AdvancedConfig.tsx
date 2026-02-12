import React from 'react';
import { Settings, ChevronDown } from 'lucide-react';

interface ScanConfig {
  profile: 'quick' | 'standard' | 'full' | 'aggressive' | 'custom';
  maxUrls?: number;
  depthLimit?: number;
  timeout?: number;
  verbose: boolean;
  modules: {
    sqli: boolean;
    xss: boolean;
    csrf: boolean;
  };
  customPayloads?: {
    sqli?: string[];
    xss?: string[];
  };
}

interface AdvancedConfigProps {
  config: ScanConfig;
  onConfigChange: (config: ScanConfig) => void;
  isOpen: boolean;
  onToggle: () => void;
}

const profileDescriptions = {
  quick: 'Fast scan - 10 URLs, depth 1',
  standard: 'Balanced - 30 URLs, depth 2 (Recommended)',
  full: 'Comprehensive - 100 URLs, depth 3',
  aggressive: 'Maximum - 200 URLs, depth 5',
  custom: 'Custom configuration'
};

export function AdvancedConfig({ config, onConfigChange, isOpen, onToggle }: AdvancedConfigProps) {
  const handleProfileChange = (profile: ScanConfig['profile']) => {
    const profileDefaults = {
      quick: { maxUrls: 10, depthLimit: 1, timeout: 5 },
      standard: { maxUrls: 30, depthLimit: 2, timeout: 8 },
      full: { maxUrls: 100, depthLimit: 3, timeout: 15 },
      aggressive: { maxUrls: 200, depthLimit: 5, timeout: 20 },
      custom: { maxUrls: 30, depthLimit: 2, timeout: 8 }
    };

    const defaults = profileDefaults[profile];
    onConfigChange({
      ...config,
      profile,
      ...defaults
    });
  };

  const handleModuleToggle = (module: 'sqli' | 'xss' | 'csrf') => {
    onConfigChange({
      ...config,
      modules: {
        ...config.modules,
        [module]: !config.modules[module]
      }
    });
  };

  return (
    <div className="border-t border-gray-200">
      <button
        onClick={onToggle}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Settings size={20} className="text-gray-600" />
          <span className="font-medium text-gray-700">Advanced Configuration</span>
        </div>
        <ChevronDown
          size={20}
          className={`text-gray-600 transition-transform ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {isOpen && (
        <div className="px-6 py-6 bg-gray-50 border-t border-gray-200 space-y-6">
          {/* Scan Profile */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Scan Profile
            </label>
            <div className="grid grid-cols-2 gap-3">
              {(Object.keys(profileDescriptions) as Array<keyof typeof profileDescriptions>).map((prof) => (
                <button
                  key={prof}
                  onClick={() => handleProfileChange(prof)}
                  className={`p-3 rounded-lg border-2 transition-all text-left ${
                    config.profile === prof
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium text-sm text-gray-900 capitalize">{prof}</div>
                  <div className="text-xs text-gray-600">{profileDescriptions[prof]}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Vulnerability Modules */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Vulnerability Modules
            </label>
            <div className="space-y-2">
              {(['sqli', 'xss', 'csrf'] as const).map((module) => (
                <label key={module} className="flex items-center gap-3 p-3 rounded-lg hover:bg-white cursor-pointer transition-colors">
                  <input
                    type="checkbox"
                    checked={config.modules[module]}
                    onChange={() => handleModuleToggle(module)}
                    className="w-4 h-4 rounded border-gray-300 text-blue-600"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    {module === 'sqli' && 'SQL Injection (SQLi)'}
                    {module === 'xss' && 'Cross-Site Scripting (XSS)'}
                    {module === 'csrf' && 'Cross-Site Request Forgery (CSRF)'}
                  </span>
                </label>
              ))}
            </div>
          </div>

          {/* Custom Parameters */}
          {config.profile === 'custom' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Maximum URLs ({config.maxUrls})
                </label>
                <input
                  type="range"
                  min="5"
                  max="200"
                  value={config.maxUrls || 30}
                  onChange={(e) =>
                    onConfigChange({
                      ...config,
                      maxUrls: parseInt(e.target.value)
                    })
                  }
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Depth Limit ({config.depthLimit})
                </label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={config.depthLimit || 2}
                  onChange={(e) =>
                    onConfigChange({
                      ...config,
                      depthLimit: parseInt(e.target.value)
                    })
                  }
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Request Timeout ({config.timeout}s)
                </label>
                <input
                  type="range"
                  min="5"
                  max="30"
                  value={config.timeout || 8}
                  onChange={(e) =>
                    onConfigChange({
                      ...config,
                      timeout: parseInt(e.target.value)
                    })
                  }
                  className="w-full"
                />
              </div>
            </div>
          )}

          {/* Verbose Mode */}
          <div>
            <label className="flex items-center gap-3 p-3 rounded-lg hover:bg-white cursor-pointer transition-colors">
              <input
                type="checkbox"
                checked={config.verbose}
                onChange={(e) =>
                  onConfigChange({
                    ...config,
                    verbose: e.target.checked
                  })
                }
                className="w-4 h-4 rounded border-gray-300 text-blue-600"
              />
              <span className="text-sm font-medium text-gray-700">
                Enable Verbose Logging
              </span>
            </label>
          </div>
        </div>
      )}
    </div>
  );
}
