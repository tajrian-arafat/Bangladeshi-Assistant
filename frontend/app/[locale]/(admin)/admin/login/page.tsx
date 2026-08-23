"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "@/i18n/routing";
import { useTranslations } from "next-intl";
import { api, ApiClientError } from "@/lib/api";

export default function AdminLoginPage() {
  const t = useTranslations("admin");
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await api.adminLogin({ email, password });
      localStorage.setItem("bda_admin_token", response.access_token);
      router.push("/admin");
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(t("loginError"));
      } else {
        setError(t("loginError"));
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-bd-green-500 text-2xl text-white">
            🇧🇩
          </div>
          <h1 className="text-2xl font-bold text-gray-900">{t("login")}</h1>
          <p className="mt-2 text-sm text-gray-500">{t("loginSubtitle")}</p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
        >
          {error && (
            <div
              className="mb-4 rounded-lg border border-bd-red-200 bg-bd-red-50 px-4 py-3 text-sm text-bd-red-700"
              role="alert"
            >
              {error}
            </div>
          )}

          <div className="mb-4">
            <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-gray-700">
              {t("email")}
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-bd-green-400 focus:outline-none focus:ring-2 focus:ring-bd-green-100"
            />
          </div>

          <div className="mb-6">
            <label htmlFor="password" className="mb-1.5 block text-sm font-medium text-gray-700">
              {t("password")}
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm focus:border-bd-green-400 focus:outline-none focus:ring-2 focus:ring-bd-green-100"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-bd-green-500 py-2.5 text-sm font-medium text-white transition-colors hover:bg-bd-green-600 disabled:opacity-50"
          >
            {loading ? t("signingIn") : t("signIn")}
          </button>
        </form>
      </div>
    </div>
  );
}
