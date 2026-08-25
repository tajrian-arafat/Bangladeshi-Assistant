import { getTranslations } from "next-intl/server";

export default async function PrivacyPage() {
  const t = await getTranslations("privacy");

  const sections = [
    { title: t("dataCollection"), text: t("dataCollectionText") },
    { title: t("documents"), text: t("documentsText") },
    { title: t("noSelling"), text: t("noSellingText") },
    { title: t("contact"), text: t("contactText") },
  ];

  return (
    <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
      <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl">{t("title")}</h1>
      <p className="mt-4 leading-relaxed text-gray-600">{t("intro")}</p>

      <div className="mt-10 space-y-8">
        {sections.map((section) => (
          <section key={section.title}>
            <h2 className="text-lg font-semibold text-gray-900">{section.title}</h2>
            <p className="mt-2 leading-relaxed text-gray-600">{section.text}</p>
          </section>
        ))}
      </div>
    </div>
  );
}
