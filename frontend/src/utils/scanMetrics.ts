import { ScanResult } from '../types';

export type VulnerabilityCounts = {
  sqli: number;
  xss: number;
  csrf: number;
  total: number;
};

export type RiskLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export const RISK_STYLES: Record<RiskLevel, { text: string; bg: string; border: string }> = {
  CRITICAL: { text: 'text-red-600', bg: 'bg-red-50', border: 'border-red-600' },
  HIGH: { text: 'text-orange-600', bg: 'bg-orange-50', border: 'border-orange-600' },
  MEDIUM: { text: 'text-yellow-600', bg: 'bg-yellow-50', border: 'border-yellow-600' },
  LOW: { text: 'text-green-600', bg: 'bg-green-50', border: 'border-green-600' },
};

export const getVulnerabilityCounts = (
  result: Pick<ScanResult, 'vulnerabilities'>,
): VulnerabilityCounts => {
  const sqli = result.vulnerabilities?.sqli?.length || 0;
  const xss = result.vulnerabilities?.xss?.length || 0;
  const csrf = result.vulnerabilities?.csrf?.length || 0;

  return { sqli, xss, csrf, total: sqli + xss + csrf };
};

export const getTotalUrls = (result: ScanResult): number => {
  return result.sitemapData?.totalUrls ?? result.sitemap_urls?.length ?? 0;
};

export const getRiskLevel = (counts: Pick<VulnerabilityCounts, 'sqli' | 'xss' | 'csrf'>): RiskLevel => {
  if (counts.sqli > 0) return 'CRITICAL';
  if (counts.xss > 0) return 'HIGH';
  if (counts.csrf > 0) return 'MEDIUM';
  return 'LOW';
};

export const getRiskInfo = (counts: Pick<VulnerabilityCounts, 'sqli' | 'xss' | 'csrf'>) => {
  const level = getRiskLevel(counts);
  return { level, ...RISK_STYLES[level] };
};
