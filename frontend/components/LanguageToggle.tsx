"use client";

import { useLocale } from "next-intl";
import { useRouter, usePathname } from "@/i18n/routing";
import { useTranslations } from "next-intl";
import type { Locale } from "@/i18n/routing";

export function LanguageToggle() {
  const locale = useLocale() as Locale;
  const router = useRouter();
  const pathname = usePathname();
  const t = useTranslations("language");

  function switchLocale(next: Locale) {
    router.replace(pathname, { locale: next });
  }

  return (
    <div
      className="inline-flex rounded-lg border border-gray-200 bg-white p-0.5"
      role="group"
      aria-label={t("toggle")}
    >
      {(["en", "bn"] as const).map((loc) => (
        <button
          key={loc}
          type="button"
          onClick={() => switchLocale(loc)}
          className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
            locale === loc
              ? "bg-bd-green-500 text-white"
              : "text-gray-600 hover:bg-gray-50"
          }`}
          aria-pressed={locale === loc}
          lang={loc}
        >
          {t(loc)}
        </button>
      ))}
    </div>
  );
}
