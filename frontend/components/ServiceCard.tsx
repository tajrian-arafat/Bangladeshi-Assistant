"use client";

import type { ServiceSummary } from "@/types/api";
import { Link } from "@/i18n/routing";
import { useLocale } from "next-intl";

interface ServiceCardProps {
  service: ServiceSummary;
}

export function ServiceCard({ service }: ServiceCardProps) {
  const locale = useLocale();
  const title = locale === "bn" ? service.title_bn : service.title_en;
  const description =
    locale === "bn" ? service.description_bn : service.description_en;

  return (
    <article className="group flex flex-col rounded-xl border border-gray-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
      <div className="mb-3 flex items-start justify-between gap-2">
        <h3 className="text-base font-semibold text-gray-900 group-hover:text-bd-green-600">
          <Link href={`/services/${service.slug}`} className="focus:outline-none focus:underline">
            {title}
          </Link>
        </h3>
        {service.category && (
          <span className="shrink-0 rounded-full bg-bd-green-50 px-2 py-0.5 text-xs font-medium text-bd-green-700">
            {service.category}
          </span>
        )}
      </div>

      {description && (
        <p className="mb-4 flex-1 text-sm text-gray-600 line-clamp-2">{description}</p>
      )}

      <div className="flex items-center justify-between gap-2">
        {service.agency_name && (
          <span className="text-xs text-gray-500">{service.agency_name}</span>
        )}
        <Link
          href={`/services/${service.slug}`}
          className="ml-auto text-sm font-medium text-bd-green-600 hover:text-bd-green-800 hover:underline"
        >
          →
        </Link>
      </div>
    </article>
  );
}
