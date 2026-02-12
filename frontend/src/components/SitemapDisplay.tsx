import React from 'react';
import { Map, CheckCircle2 } from 'lucide-react';

interface SitemapDisplayProps {
  sitemapImage?: string;
  totalUrls: number;
}

export const SitemapDisplay: React.FC<SitemapDisplayProps> = ({
  sitemapImage,
  totalUrls,
}) => {
  const hasSitemap = Boolean(sitemapImage);

  return (
    <div className="w-full space-y-5 rounded-xl border border-sky-100 bg-gradient-to-br from-sky-50 via-white to-cyan-50 p-5">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-gray-900 font-bold text-lg">
          <Map className="h-6 w-6 text-sky-700" />
          <span>Sitemap Overview</span>
        </div>
        <div className="inline-flex items-center gap-2 rounded-full bg-sky-100 px-3 py-1 text-xs font-semibold text-sky-800">
          <CheckCircle2 className="h-4 w-4" />
          English Report View
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-lg border border-sky-200 bg-sky-100 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-sky-800">Total URLs</p>
          <p className="mt-1 text-3xl font-bold text-sky-900">{totalUrls}</p>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4 md:col-span-2">
          <p className="text-sm text-gray-700 leading-relaxed">
            Sitemap visualization helps verify crawl coverage and identify paths where vulnerabilities may exist.
          </p>
        </div>
      </div>

      {hasSitemap && (
        <div className="overflow-hidden rounded-xl border border-sky-200 bg-white shadow-sm">
          <div className="border-b border-sky-100 bg-sky-50 px-4 py-2 text-sm font-semibold text-sky-900">
            Generated Sitemap Image
          </div>
          <img
            src={sitemapImage}
            alt="Generated website sitemap"
            className="w-full h-auto max-h-[28rem] object-contain bg-white p-2"
          />
        </div>
      )}

      {!hasSitemap && (
        <div className="rounded-lg border border-dashed border-gray-300 bg-white p-4 text-sm text-gray-600">
          No sitemap image is available for this scan. URL coverage metrics are still shown above.
        </div>
      )}
    </div>
  );
};
