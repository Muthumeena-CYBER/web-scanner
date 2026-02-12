export interface ScanResult {
  url: string;
  timestamp: string;
  profile?: string;
  success?: boolean;
  scan_start_time?: string;
  scan_end_time?: string;
  scan_duration_seconds?: number;
  server?: {
    type?: string;
    header?: string;
  };
  performance?: {
    total_requests_sent?: number;
    total_responses_received?: number;
    average_response_time_ms?: number;
    scan_mode?: 'Sync' | 'Async' | string;
    thread_count_used?: number;
    errors_encountered?: number;
    total_forms_detected?: number;
    total_input_parameters_tested?: number;
    payload_metrics?: {
      total_payloads_tested?: number;
      successful_payloads?: number;
      blocked_payloads?: number;
      entries?: Array<{
        vulnerabilityType: 'SQL Injection' | 'Cross-Site Scripting' | 'CSRF';
        payloadUsed: string;
        status: 'Successful' | 'Blocked' | 'Detected';
        responseCode: number | string;
      }>;
    };
  };
  vulnerabilities: {
    sqli: VulnerabilityFinding[];
    xss: VulnerabilityFinding[];
    csrf: VulnerabilityFinding[];
  };
  sitemapData?: {
    urls: string[];
    totalUrls: number;
    sitemapImage?: string;
  };
  sitemap_urls?: string[];
  summary?: {
    sqli_found?: boolean;
    xss_found?: boolean;
    csrf_found?: boolean;
    total_vulnerabilities?: number;
    sqli_count?: number;
    xss_count?: number;
    csrf_count?: number;
  };
}

export interface VulnerabilityFinding {
  param?: string;
  parameter?: string;
  formName?: string;
  component?: string;
  payload?: string;
  vulnerability_type?: string;
  type?: string;
  severity?: string;
  details?: string;
  message?: string;
  url?: string;
}

export interface ScanOptions {
  url: string;
  checkSQLi: boolean;
  checkXSS: boolean;
  checkCSRF: boolean;
  profile?: 'quick' | 'standard' | 'full' | 'aggressive' | 'custom';
  customConfig?: {
    maxUrls?: number;
    depthLimit?: number;
    timeout?: number;
    verbose?: boolean;
    modules?: {
      sqli: boolean;
      xss: boolean;
      csrf: boolean;
    };
    customPayloads?: {
      sqli?: string[];
      xss?: string[];
    };
  };
}
