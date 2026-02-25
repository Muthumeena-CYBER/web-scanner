export interface ScanResult {
  url: string;
  timestamp: string;
  target?: string;
  scan_time?: string;
  overall_risk_score?: 'Low' | 'Medium' | 'High' | string;
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
  web_vulnerabilities?: {
    sqli: VulnerabilityFinding[];
    xss: VulnerabilityFinding[];
    csrf: VulnerabilityFinding[];
  };
  port_scan_results?: {
    target_host?: string;
    target_ip?: string;
    total_ports_scanned?: number;
    open_ports_count?: number;
    open_ports?: Array<{
      port: number;
      service_guess: string;
      risk: 'Low' | 'Medium' | 'High' | string;
    }>;
    risk_summary?: 'Low' | 'Medium' | 'High' | string;
    safety_warning?: string;
    scan_status?: 'completed' | 'blocked' | 'error' | 'skipped' | string;
    reason?: string;
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
  authorizationConfirmed?: boolean;
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
