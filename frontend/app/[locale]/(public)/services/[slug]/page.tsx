"use client";

import { use } from "react";
import { useTranslations, useLocale } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { Link } from "@/i18n/routing";
import { ChecklistView } from "@/components/ChecklistView";
import { ProcedureSteps } from "@/components/ProcedureSteps";
import { ConfidenceBadge } from "@/components/ConfidenceBadge";
import { api } from "@/lib/api";

interface ServiceDetailPageProps {
  params: Promise<{ slug: string }>;
}

export default function ServiceDetailPage({ params }: ServiceDetailPageProps) {
  const { slug } = use(params);
  const t = useTranslations("services");
  const tCommon = useTranslations("common");
  const locale = useLocale();

  const { data: service, isLoading, isError, refetch } = useQuery({
    queryKey: ["service", slug],
    queryFn: () => api.getService(slug),
  });

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <p className="text-sm text-gray-500" role="status">
          {tCommon("loading")}
        </p>
      </div>
    );
  }

  if (isError || !service) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 text-center">
        <p className="text-gray-600">{tCommon("error")}</p>
        <button
          type="button"
          onClick={() => refetch()}
          className="mt-4 text-sm font-medium text-bd-green-600 hover:underline"
        >
          {tCommon("retry")}
        </button>
        <Link href="/services" className="mt-4 block text-sm text-gray-500 hover:underline">
          ← {t("title")}
        </Link>
      </div>
    );
  }

  const title = locale === "bn" ? service.name_bn : service.name_en;
  const checklist = (service.checklist_items ?? []).map((item) => ({
    item: locale === "bn" ? item.label_bn : item.label_en,
    type: item.item_type as "REQUIRED" | "OPTIONAL" | "CONDITIONAL" | "RECOMMENDED" | "NOT_APPLICABLE",
  }));
  const steps = (service.procedure_steps ?? []).map((step) => ({
    order: step.order,
    title: locale === "bn" ? step.title_bn : step.title_en,
    description: locale === "bn" ? step.description_bn : step.description_en,
    official_url: step.official_url,
  }));

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <Link
        href="/services"
        className="mb-6 inline-flex items-center text-sm text-gray-500 hover:text-bd-green-600"
      >
        ← {t("title")}
      </Link>

      <header className="mb-8">
        <div className="mb-3 flex flex-wrap items-center gap-2">
          {service.category && (
            <span className="rounded-full bg-bd-green-50 px-3 py-1 text-xs font-medium text-bd-green-700">
              {service.category}
            </span>
          )}
          {service.status && (
            <span className="text-sm text-gray-500">{service.status}</span>
          )}
        </div>
        <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">{title}</h1>
        {service.last_verified_at && (
          <p className="mt-2 text-xs text-gray-400">
            {t("lastVerified")}:{" "}
            {new Date(service.last_verified_at).toLocaleDateString(
              locale === "bn" ? "bn-BD" : "en-US",
            )}
          </p>
        )}
      </header>

      <div className="space-y-8">
        {checklist.length > 0 && (
          <section className="rounded-xl border border-gray-200 bg-white p-6">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("requirements")}</h2>
            <ChecklistView items={checklist} />
          </section>
        )}

        {steps.length > 0 && (
          <section className="rounded-xl border border-gray-200 bg-white p-6">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("relatedProcedures")}</h2>
            <ProcedureSteps steps={steps} />
          </section>
        )}

        {service.fees && service.fees.length > 0 && (
          <section className="rounded-xl border border-gray-200 bg-white p-6">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Fees</h2>
            <ul className="space-y-2">
              {service.fees.map((fee, i) => (
                <li key={i} className="flex items-center justify-between rounded-lg bg-gray-50 px-4 py-3 text-sm">
                  <span>{fee.label ?? "Fee"}</span>
                  <span className="font-semibold text-bd-green-700">
                    {fee.amount} {fee.currency}
                  </span>
                </li>
              ))}
            </ul>
            <div className="mt-3">
              <ConfidenceBadge level="medium" size="sm" showDescription />
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
