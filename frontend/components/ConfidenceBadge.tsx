"use client";

import type { ConfidenceLevel } from "@/types/api";
import { useTranslations } from "next-intl";

const styles: Record<ConfidenceLevel, string> = {
  high: "bg-bd-green-100 text-bd-green-800 border-bd-green-300",
  medium: "bg-amber-100 text-amber-800 border-amber-300",
  low: "bg-orange-100 text-orange-800 border-orange-300",
  conflicted: "bg-bd-red-100 text-bd-red-800 border-bd-red-300",
  unavailable: "bg-gray-100 text-gray-600 border-gray-300",
};

interface ConfidenceBadgeProps {
  level: ConfidenceLevel;
  showDescription?: boolean;
  size?: "sm" | "md";
}

export function ConfidenceBadge({
  level,
  showDescription = false,
  size = "md",
}: ConfidenceBadgeProps) {
  const t = useTranslations("confidence");

  const sizeClass = size === "sm" ? "text-xs px-2 py-0.5" : "text-sm px-3 py-1";

  return (
    <div className="inline-flex flex-col gap-1">
      <span
        className={`inline-flex items-center gap-1.5 rounded-full border font-medium ${styles[level]} ${sizeClass}`}
        role="status"
        aria-label={t(level)}
      >
        <span
          className={`h-2 w-2 rounded-full ${
            level === "high"
              ? "bg-bd-green-500"
              : level === "medium"
                ? "bg-amber-500"
                : level === "low"
                  ? "bg-orange-500"
                  : level === "conflicted"
                    ? "bg-bd-red-500"
                    : "bg-gray-400"
          }`}
          aria-hidden="true"
        />
        {t(level)}
      </span>
      {showDescription && (
        <span className="text-xs text-gray-600">{t(`${level}Desc`)}</span>
      )}
    </div>
  );
}
