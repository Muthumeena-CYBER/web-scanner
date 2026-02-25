import axios from 'axios';
import { ScanOptions, ScanResult } from '../types';

export const API_BASE = 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 300000, // 5 minute timeout for scanning
});

const buildScanPayload = (options: ScanOptions) => {
  const moduleList = options.customConfig?.modules
    ? Object.entries(options.customConfig.modules)
        .filter(([, enabled]) => enabled)
        .map(([name]) => name)
    : undefined;

  const customConfig = options.customConfig
    ? {
        max_urls: options.customConfig.maxUrls,
        depth_limit: options.customConfig.depthLimit,
        timeout: options.customConfig.timeout,
        verbose: options.customConfig.verbose,
        modules: moduleList,
        custom_payloads: options.customConfig.customPayloads,
      }
    : undefined;

  return {
    url: options.url,
    profile: options.profile,
    authorization_confirmed: !!options.authorizationConfirmed,
    custom_config: customConfig,
    check_sqli: options.checkSQLi,
    check_xss: options.checkXSS,
    check_csrf: options.checkCSRF,
  };
};

export const scannerAPI = {
  scan: async (options: ScanOptions): Promise<ScanResult> => {
    try {
      const response = await api.post('/scan', buildScanPayload(options));
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Scan failed');
    }
  },
  scanAsync: async (options: ScanOptions): Promise<{ scan_id: string }> => {
    try {
      const response = await api.post('/scan/async', buildScanPayload(options));
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to start async scan');
    }
  },
  getScanStatus: async (scanId: string) => {
    try {
      const response = await api.get('/scan/status', { params: { scan_id: scanId } });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to fetch scan status');
    }
  },
  stopScan: async (scanId: string) => {
    try {
      const response = await api.post('/scan/stop', { scan_id: scanId });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to stop scan');
    }
  },
  generateReport: async (payload: {
    url: string;
    format: 'json' | 'csv' | 'html';
    vulnerabilities: ScanResult['vulnerabilities'];
    sitemap_urls?: string[];
    profile?: string;
  }) => {
    try {
      const response = await api.post('/report', payload);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to generate report');
    }
  },

  getSitemap: async (url: string) => {
    try {
      const response = await api.get('/sitemap', { params: { url } });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to fetch sitemap');
    }
  },

  downloadPDF: async (payload: { url: string; vulnerabilities?: ScanResult['vulnerabilities']; timestamp?: string }) => {
    try {
      const response = await api.post('/download-pdf', payload);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Failed to download PDF');
    }
  },
};
