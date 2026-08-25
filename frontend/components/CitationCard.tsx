"use client";

import type { Citation } from "@/types/api";
import { useTranslations } from "next-intl";

interface CitationCardProps {
  citation: Citation;
  index?: number;
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return iso;
  }
}

export function CitationCard({ citation, index }: CitationCardProps) {
  const t = useTranslations("citation");
  const tCommon = useTranslations("common");

  return (
    <article
      className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
      aria-labelledby={index !== undefined ? `citation-${index}` : undefined}
    >
      <div className="mb-2 flex flex-wrap items-start justify-between gap-2">
        <h4
          id={index !== undefined ? `citation-${index}` : undefined}
          className="text-sm font-semibold text-gray-900"
        >
          {citation.source_title}
        </h4>
        <span className="rounded bg-bd-green-50 px-2 py-0.5 text-xs font-medium text-bd-green-700">
          {t("tier")} {citation.tier}
        </span>
      </div>

      {citation.excerpt && (
        <blockquote className="mb-3 border-l-2 border-bd-green-300 pl-3 text-sm italic text-gray-600">
          &ldquo;{citation.excerpt}&rdquo;
        </blockquote>
      )}

      <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-gray-500">
        <span>
          {tCommon("lastVerified")}: {formatDate(citation.last_verified_at)}
        </span>
        <a
          href={citation.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 font-medium text-bd-green-600 hover:text-bd-green-800 hover:underline"
        >
          {t("viewSource")}
          <svg
            className="h-3 w-3"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
            />
          </svg>
        </a>
      </div>
    </article>
  );
}
