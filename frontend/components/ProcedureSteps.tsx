"use client";

import type { ProcedureStep } from "@/types/api";
import { useTranslations } from "next-intl";

interface ProcedureStepsProps {
  steps: ProcedureStep[];
}

export function ProcedureSteps({ steps }: ProcedureStepsProps) {
  const t = useTranslations("chat");

  if (steps.length === 0) return null;

  return (
    <section aria-labelledby="steps-heading">
      <h3 id="steps-heading" className="mb-3 text-sm font-semibold text-gray-900">
        {t("steps")}
      </h3>
      <ol className="space-y-3" role="list">
        {steps.map((step) => (
          <li key={step.order} className="flex gap-3">
            <span
              className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-bd-green-500 text-sm font-bold text-white"
              aria-hidden="true"
            >
              {step.order}
            </span>
            <div className="flex-1 pt-0.5">
              <p className="text-sm font-medium text-gray-900">{step.title}</p>
              {step.description && (
                <p className="mt-1 text-sm text-gray-600">{step.description}</p>
              )}
              {step.official_url && (
                <a
                  href={step.official_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-1 inline-block text-sm text-bd-green-600 hover:underline"
                >
                  {step.official_url}
                </a>
              )}
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
