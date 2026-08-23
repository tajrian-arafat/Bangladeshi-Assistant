"use client";

import { useState, useMemo } from "react";
import { useTranslations, useLocale } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function DistrictsPage() {
  const t = useTranslations("districts");
  const tCommon = useTranslations("common");
  const locale = useLocale();
  const [search, setSearch] = useState("");

  const { data: districts, isLoading, isError, refetch } = useQuery({
    queryKey: ["districts"],
    queryFn: api.getDistricts,
  });

  const filtered = useMemo(() => {
    if (!districts) return [];
    if (!search.trim()) return districts;
    const q = search.toLowerCase();
    return districts.filter(
      (d) =>
        d.name_en.toLowerCase().includes(q) ||
        d.name_bn.includes(search) ||
        d.division_name_en?.toLowerCase().includes(q),
    );
  }, [districts, search]);

  const grouped = useMemo(() => {
    const map = new Map<string, typeof filtered>();
    for (const d of filtered) {
      const key =
        locale === "bn"
          ? (d.division_name_bn ?? d.division_name_en ?? "Other")
          : (d.division_name_en ?? "Other");
      const list = map.get(key) ?? [];
      list.push(d);
      map.set(key, list);
    }
    return Array.from(map.entries()).sort(([a], [b]) => a.localeCompare(b));
  }, [filtered, locale]);

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">{t("title")}</h1>
        <p className="mt-2 text-gray-600">{t("subtitle")}</p>
      </header>

      <div className="mb-6">
        <label htmlFor="district-search" className="sr-only">
          {t("searchPlaceholder")}
        </label>
        <input
          id="district-search"
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

      {!isLoading && !isError && filtered.length === 0 && (
        <p className="py-12 text-center text-sm text-gray-500" role="status">
          {t("empty")}
        </p>
      )}

      <div className="space-y-8">
        {grouped.map(([division, items]) => (
          <section key={division}>
            <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-bd-green-700">
              <span className="h-1 w-6 rounded bg-bd-green-500" aria-hidden="true" />
              {division}
            </h2>
            <div className="grid gap-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
              {items.map((district) => (
                <div
                  key={district.id}
                  className="rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm transition-colors hover:border-bd-green-300 hover:bg-bd-green-50"
                >
                  <span className="font-medium text-gray-900">
                    {locale === "bn" ? district.name_bn : district.name_en}
                  </span>
                  {locale === "en" && district.name_bn && (
                    <span className="mt-0.5 block text-xs text-gray-400">{district.name_bn}</span>
                  )}
                </div>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
