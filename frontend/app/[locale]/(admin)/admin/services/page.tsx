"use client";

import { useTranslations, useLocale } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function AdminServicesPage() {
  const t = useTranslations("admin");
  const tCommon = useTranslations("common");
  const locale = useLocale();

  const { data: services, isLoading, isError, refetch } = useQuery({
    queryKey: ["admin-services"],
    queryFn: api.adminServices,
    retry: false,
  });

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-900 sm:text-2xl">{t("services")}</h1>

      {isLoading && (
        <p className="mt-8 text-sm text-gray-500" role="status">
          {tCommon("loading")}
        </p>
      )}

      {isError && (
        <div className="mt-8 rounded-lg border border-amber-200 bg-amber-50 p-6" role="alert">
          <p className="text-sm text-amber-800">{tCommon("error")}</p>
          <button
            type="button"
            onClick={() => refetch()}
            className="mt-3 text-sm font-medium text-bd-green-600 hover:underline"
          >
            {tCommon("retry")}
          </button>
        </div>
      )}

      {services && services.length === 0 && (
        <p className="mt-8 text-sm text-gray-500" role="status">
          {tCommon("empty")}
        </p>
      )}

      {services && services.length > 0 && (
        <div className="mt-6 overflow-x-auto rounded-xl border border-gray-200 bg-white">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-gray-200 bg-gray-50">
              <tr>
                <th className="px-4 py-3 font-medium text-gray-600">Slug</th>
                <th className="px-4 py-3 font-medium text-gray-600">Title</th>
                <th className="px-4 py-3 font-medium text-gray-600">Agency</th>
                <th className="px-4 py-3 font-medium text-gray-600">Category</th>
              </tr>
            </thead>
            <tbody>
              {services.map((service) => (
                <tr key={service.id} className="border-b border-gray-100 last:border-0">
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">{service.slug}</td>
                  <td className="px-4 py-3 font-medium text-gray-900">
                    {locale === "bn" ? service.title_bn : service.title_en}
                  </td>
                  <td className="px-4 py-3 text-gray-600">{service.agency_name ?? "—"}</td>
                  <td className="px-4 py-3">
                    {service.category ? (
                      <span className="rounded-full bg-bd-green-50 px-2 py-0.5 text-xs text-bd-green-700">
                        {service.category}
                      </span>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
