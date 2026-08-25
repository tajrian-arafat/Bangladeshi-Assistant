"use client";

import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

const priorityColors = {
  high: "bg-bd-red-100 text-bd-red-700",
  medium: "bg-amber-100 text-amber-700",
  low: "bg-gray-100 text-gray-600",
};

const statusColors = {
  pending: "bg-amber-100 text-amber-700",
  approved: "bg-bd-green-100 text-bd-green-700",
  rejected: "bg-bd-red-100 text-bd-red-700",
};

export default function AdminReviewsPage() {
  const t = useTranslations("admin");
  const tCommon = useTranslations("common");

  const { data: reviews, isLoading, isError, refetch } = useQuery({
    queryKey: ["admin-reviews"],
    queryFn: api.adminReviews,
    retry: false,
  });

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-900 sm:text-2xl">{t("reviewQueue")}</h1>

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

      {!isLoading && !isError && reviews?.length === 0 && (
        <p className="mt-8 text-sm text-gray-500" role="status">
          {t("reviewEmpty")}
        </p>
      )}

      {reviews && reviews.length > 0 && (
        <div className="mt-6 space-y-3">
          {reviews.map((item) => (
            <article
              key={item.id}
              className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm sm:p-5"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h2 className="font-semibold text-gray-900">{item.title}</h2>
                  <p className="mt-1 text-xs text-gray-500">
                    {item.type} · {new Date(item.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex gap-2">
                  {item.priority && (
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${priorityColors[item.priority]}`}
                    >
                      {t("priority")}: {item.priority}
                    </span>
                  )}
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${statusColors[item.status]}`}
                  >
                    {t("status")}: {item.status}
                  </span>
                </div>
              </div>

              {item.status === "pending" && (
                <div className="mt-4 flex gap-2">
                  <button
                    type="button"
                    className="rounded-lg bg-bd-green-500 px-4 py-1.5 text-sm font-medium text-white hover:bg-bd-green-600"
                  >
                    {t("approve")}
                  </button>
                  <button
                    type="button"
                    className="rounded-lg border border-gray-200 px-4 py-1.5 text-sm font-medium text-gray-600 hover:bg-gray-50"
                  >
                    {t("reject")}
                  </button>
                </div>
              )}
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
