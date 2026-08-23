"use client";

import { Link, usePathname } from "@/i18n/routing";
import { useTranslations } from "next-intl";
import { useRouter } from "@/i18n/routing";
import { useEffect } from "react";

const navItems = [
  { href: "/admin" as const, labelKey: "dashboard" as const },
  { href: "/admin/services" as const, labelKey: "services" as const },
  { href: "/admin/reviews" as const, labelKey: "reviews" as const },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const t = useTranslations("admin");
  const pathname = usePathname();
  const router = useRouter();
  const isLoginPage = pathname === "/admin/login";

  useEffect(() => {
    if (isLoginPage) return;
    const token = localStorage.getItem("bda_admin_token");
    if (!token) {
      router.replace("/admin/login");
    }
  }, [isLoginPage, router]);

  if (isLoginPage) {
    return (
      <div className="min-h-screen bg-gray-100">
        {children}
      </div>
    );
  }

  function handleLogout() {
    localStorage.removeItem("bda_admin_token");
    router.replace("/admin/login");
  }

  return (
    <div className="flex min-h-screen bg-gray-100">
      <aside className="relative hidden w-56 shrink-0 border-r border-gray-200 bg-white md:block">
        <div className="border-b border-gray-200 px-4 py-5">
          <p className="font-bold text-bd-green-600">{t("title")}</p>
        </div>
        <nav className="p-3" aria-label="Admin navigation">
          <ul className="space-y-1">
            {navItems.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={`block rounded-lg px-3 py-2 text-sm font-medium ${
                    pathname === item.href
                      ? "bg-bd-green-50 text-bd-green-700"
                      : "text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  {t(item.labelKey)}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        <div className="absolute bottom-0 w-56 border-t border-gray-200 p-3">
          <button
            type="button"
            onClick={handleLogout}
            className="w-full rounded-lg px-3 py-2 text-left text-sm text-gray-600 hover:bg-gray-50"
          >
            {t("logout")}
          </button>
        </div>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-gray-200 bg-white px-4 py-3 md:hidden">
          <p className="font-bold text-bd-green-600">{t("title")}</p>
          <button
            type="button"
            onClick={handleLogout}
            className="text-sm text-gray-600"
          >
            {t("logout")}
          </button>
        </header>

        <nav className="flex gap-1 overflow-x-auto border-b border-gray-200 bg-white px-4 py-2 md:hidden">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`shrink-0 rounded-lg px-3 py-1.5 text-sm font-medium ${
                pathname === item.href
                  ? "bg-bd-green-50 text-bd-green-700"
                  : "text-gray-600"
              }`}
            >
              {t(item.labelKey)}
            </Link>
          ))}
        </nav>

        <main className="flex-1 p-4 sm:p-6">{children}</main>
      </div>
    </div>
  );
}
