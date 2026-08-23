"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { ServiceCard } from "@/components/ServiceCard";
import { api } from "@/lib/api";

export default function ServicesPage() {
  const t = useTranslations("services");
  const tCommon = useTranslations("common");
  const [search, setSearch] = useState("");

  const { data: services, isLoading, isError, refetch } = useQuery({
    queryKey: ["services", search],
    queryFn: () => api.getServices(search ? { q: search } : undefined),
  });

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">{t("title")}</h1>
        <p className="mt-2 text-gray-600">{t("subtitle")}</p>
      </header>

      <div className="mb-6">
        <label htmlFor="service-search" className="sr-only">
          {t("searchPlaceholder")}
        </label>
        <input
          id="service-search"
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder={t("searchPlaceholder")}
          className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm shadow-sm focus:border-bd-green-400 focus:outline-none focus:ring-2 focus:ring-bd-green-100 sm:max-w-md"
        />
      </div>

      {isLoading && (
        <p className="py-12 text-center text-sm text-gray-500" role="status">
          {tCommon("loading")}
        </p>
      )}

      {isError && (
        <div className="rounded-lg border border-bd-red-200 bg-bd-red-50 p-6 text-center" role="alert">
          <p className="text-sm text-bd-red-700">{tCommon("error")}</p>
          <button
            type="button"
            onClick={() => refetch()}
            className="mt-3 text-sm font-medium text-bd-green-600 hover:underline"
          >
            {tCommon("retry")}
          </button>
        </div>
      )}

      {!isLoading && !isError && services?.length === 0 && (
        <p className="py-12 text-center text-sm text-gray-500" role="status">
          {t("empty")}
        </p>
      )}

      {services && services.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {services.map((service) => (
            <ServiceCard key={service.id} service={service} />
          ))}
        </div>
      )}
    </div>
  );
}
