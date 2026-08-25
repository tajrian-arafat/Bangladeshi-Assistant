"use client";

import type { ChecklistItem } from "@/types/api";
import { useTranslations } from "next-intl";

interface ChecklistViewProps {
  items: ChecklistItem[];
}

const typeStyles: Record<ChecklistItem["type"], string> = {
  REQUIRED: "bg-bd-red-50 text-bd-red-700 border-bd-red-200",
  OPTIONAL: "bg-gray-50 text-gray-600 border-gray-200",
  CONDITIONAL: "bg-amber-50 text-amber-700 border-amber-200",
  RECOMMENDED: "bg-bd-green-50 text-bd-green-700 border-bd-green-200",
  NOT_APPLICABLE: "bg-gray-50 text-gray-400 border-gray-200 line-through",
};

export function ChecklistView({ items }: ChecklistViewProps) {
  const t = useTranslations("checklist");
  const tChat = useTranslations("chat");

  if (items.length === 0) {
    return (
      <p className="text-sm text-gray-500" role="status">
        {t("empty")}
      </p>
    );
  }

  return (
    <section aria-labelledby="checklist-heading">
      <h3 id="checklist-heading" className="mb-3 text-sm font-semibold text-gray-900">
        {tChat("checklist")}
      </h3>
      <ul className="space-y-2" role="list">
        {items.map((item, i) => (
          <li
            key={`${item.item}-${i}`}
            className="flex items-start gap-3 rounded-lg border border-gray-100 bg-white p-3"
          >
            <span
              className={`mt-0.5 shrink-0 rounded border px-2 py-0.5 text-xs font-medium ${typeStyles[item.type]}`}
            >
              {t(item.type)}
            </span>
            <span className="flex-1 text-sm text-gray-800">{item.item}</span>
            {item.confidence && item.confidence !== "high" && (
              <span className="shrink-0 text-xs text-amber-600" title={item.confidence}>
                ⚠
              </span>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
