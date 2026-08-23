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

  const title = locale === "bn" ? service.title_bn : service.title_en;
  const description =
    locale === "bn" ? service.description_bn : service.description_en;

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
          {service.agency_name && (
            <span className="text-sm text-gray-500">{service.agency_name}</span>
          )}
        </div>
        <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">{title}</h1>
        {description && (
          <p className="mt-3 text-gray-600">{description}</p>
        )}
        {service.last_verified_at && (
          <p className="mt-2 text-xs text-gray-400">
            {t("lastVerified")}:{" "}
            {new Date(service.last_verified_at).toLocaleDateString(
              locale === "bn" ? "bn-BD" : "en-US",
            )}
          </p>
        )}
      </header>

      {service.official_url && (
        <a
          href={service.official_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mb-8 inline-flex items-center gap-2 rounded-lg bg-bd-green-500 px-5 py-2.5 text-sm font-medium text-white hover:bg-bd-green-600"
        >
          {t("officialLink")}
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      )}

      <div className="space-y-8">
        {service.checklist && service.checklist.length > 0 && (
          <section className="rounded-xl border border-gray-200 bg-white p-6">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("requirements")}</h2>
            <ChecklistView items={service.checklist} />
          </section>
        )}

        {service.procedures && service.procedures.length > 0 && (
          <section className="rounded-xl border border-gray-200 bg-white p-6">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">{t("relatedProcedures")}</h2>
            <ProcedureSteps steps={service.procedures} />
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
