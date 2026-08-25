import { getTranslations } from "next-intl/server";

export default async function AboutPage() {
  const t = await getTranslations("about");

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">{t("title")}</h1>
      <p className="mt-4 leading-relaxed text-gray-600">{t("intro")}</p>

      <section className="mt-10">
        <h2 className="text-xl font-semibold text-bd-green-700">{t("missionTitle")}</h2>
        <p className="mt-3 leading-relaxed text-gray-600">{t("mission")}</p>
      </section>

      <section className="mt-10">
        <h2 className="text-xl font-semibold text-bd-green-700">{t("howTitle")}</h2>
        <ol className="mt-4 space-y-3">
          {[t("how1"), t("how2"), t("how3")].map((item, i) => (
            <li key={i} className="flex gap-3 text-gray-600">
              <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-bd-green-100 text-xs font-bold text-bd-green-700">
                {i + 1}
              </span>
              {item}
            </li>
          ))}
        </ol>
      </section>

      <section className="mt-10 rounded-xl border border-amber-200 bg-amber-50 p-6">
        <h2 className="text-lg font-semibold text-amber-800">{t("disclaimerTitle")}</h2>
        <p className="mt-2 text-sm leading-relaxed text-amber-700">{t("disclaimer")}</p>
      </section>
    </div>
  );
}
