"use client";

import type { ServiceSummary } from "@/types/api";
import { Link } from "@/i18n/routing";
import { useLocale } from "next-intl";

interface ServiceCardProps {
  service: ServiceSummary;
}

export function ServiceCard({ service }: ServiceCardProps) {
  const locale = useLocale();
  const title = locale === "bn" ? service.name_bn : service.name_en;

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

      {service.category && (
        <p className="mb-4 flex-1 text-sm text-gray-600 line-clamp-2">{service.category}</p>
      )}

      <div className="flex items-center justify-between gap-2">
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
