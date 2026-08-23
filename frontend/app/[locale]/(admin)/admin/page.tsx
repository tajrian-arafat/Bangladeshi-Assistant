"use client";

import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function AdminDashboardPage() {
  const t = useTranslations("admin");
  const tCommon = useTranslations("common");

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["admin-dashboard"],
    queryFn: api.adminDashboard,
    retry: false,
  });

  const stats = [
    { label: t("servicesCount"), value: data?.services_count ?? "—", color: "bg-bd-green-500" },
    { label: t("pendingReviews"), value: data?.pending_reviews ?? "—", color: "bg-bd-red-500" },
    { label: t("sourcesCount"), value: data?.sources_count ?? "—", color: "bg-bd-gold" },
    { label: t("systemHealth"), value: data?.health ?? "—", color: "bg-gray-500" },
  ];

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-900 sm:text-2xl">{t("dashboard")}</h1>

      {isLoading && (
        <p className="mt-8 text-sm text-gray-500" role="status">
          {tCommon("loading")}
        </p>
      )}

      {isError && (
        <div className="mt-8 rounded-lg border border-amber-200 bg-amber-50 p-6" role="alert">
          <p className="text-sm text-amber-800">
            Backend unavailable. Dashboard stats will appear when the API is running.
          </p>
          <button
            type="button"
            onClick={() => refetch()}
            className="mt-3 text-sm font-medium text-bd-green-600 hover:underline"
          >
            {tCommon("retry")}
          </button>
        </div>
      )}

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
          >
            <div className="flex items-center gap-3">
              <span className={`h-3 w-3 rounded-full ${stat.color}`} aria-hidden="true" />
              <span className="text-sm text-gray-500">{stat.label}</span>
            </div>
            <p className="mt-2 text-2xl font-bold text-gray-900">{stat.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
