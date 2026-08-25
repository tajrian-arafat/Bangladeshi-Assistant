"use client";

import { useTranslations } from "next-intl";

interface ConflictWarningProps {
  warnings: string[];
}

export function ConflictWarning({ warnings }: ConflictWarningProps) {
  const t = useTranslations("conflict");

  if (warnings.length === 0) return null;

  return (
    <div
      className="rounded-lg border border-bd-red-300 bg-bd-red-50 p-4"
      role="alert"
      aria-live="polite"
    >
      <div className="flex gap-3">
        <svg
          className="h-5 w-5 shrink-0 text-bd-red-500"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
        <div>
          <h4 className="text-sm font-semibold text-bd-red-800">{t("title")}</h4>
          <p className="mt-1 text-sm text-bd-red-700">{t("description")}</p>
          <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-bd-red-700">
            {warnings.map((warning, i) => (
              <li key={i}>{warning}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
