import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/routing";

export async function Footer() {
  const t = await getTranslations("nav");
  const tFooter = await getTranslations("footer");
  const tCommon = await getTranslations("common");

  return (
    <footer className="border-t border-gray-200 bg-gray-50">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <div className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="font-semibold text-bd-green-600">{tCommon("appName")}</p>
            <p className="mt-1 text-sm text-gray-500">{tFooter("disclaimer")}</p>
          </div>

          <nav className="flex flex-wrap gap-4 text-sm" aria-label="Footer navigation">
            <Link href="/services" className="text-gray-600 hover:text-bd-green-600">
              {t("services")}
            </Link>
            <Link href="/districts" className="text-gray-600 hover:text-bd-green-600">
              {t("districts")}
            </Link>
            <Link href="/about" className="text-gray-600 hover:text-bd-green-600">
              {t("about")}
            </Link>
            <Link href="/privacy" className="text-gray-600 hover:text-bd-green-600">
              {t("privacy")}
            </Link>
          </nav>
        </div>

        <div className="mt-6 flex items-center gap-2 border-t border-gray-200 pt-6">
          <span className="h-1 w-8 rounded bg-bd-green-500" aria-hidden="true" />
          <span className="h-1 w-4 rounded bg-bd-red-500" aria-hidden="true" />
          <p className="ml-2 text-xs text-gray-400">
            © {new Date().getFullYear()} {tCommon("appName")}. {tFooter("rights")}.
          </p>
        </div>
      </div>
    </footer>
  );
}
