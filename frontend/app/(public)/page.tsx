"use client";

import { useState, useCallback } from "react";
import { useRouter } from "@/i18n/routing";
import { useTranslations, useLocale } from "next-intl";
import { useMutation } from "@tanstack/react-query";
import { ChatThread } from "@/components/ChatThread";
import { ChatInput } from "@/components/ChatInput";
import { api, ApiClientError } from "@/lib/api";
import type { ConversationMessage } from "@/types/api";

export default function LandingPage() {
  const t = useTranslations("landing");
  const tChat = useTranslations("chat");
  const tCommon = useTranslations("common");
  const locale = useLocale();
  const router = useRouter();

  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [fallbackMode, setFallbackMode] = useState(false);

  const chatMutation = useMutation({
    mutationFn: api.chat,
    onSuccess: (data) => {
      setConversationId(data.conversation_id);
      setFallbackMode(data.metadata?.fallback_mode ?? false);

      const assistantMsg: ConversationMessage = {
        id: data.message_id,
        role: "assistant",
        content: data.answer.summary,
        confidence: data.confidence,
        answer: data.answer,
        citations: data.citations,
      };

      setMessages((prev) => [...prev, assistantMsg]);

      if (!conversationId && data.conversation_id) {
        router.push(`/chat/${data.conversation_id}`);
      }
    },
    onError: (err: Error) => {
      if (err instanceof ApiClientError) {
        setError(err.message);
      } else {
        setError(tCommon("error"));
      }
    },
  });

  const handleSend = useCallback(
    (message: string) => {
      setError(null);

      const userMsg: ConversationMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content: message,
      };
      setMessages((prev) => [...prev, userMsg]);

      chatMutation.mutate({
        message,
        conversation_id: conversationId,
        language_preference: locale === "bn" ? "bn" : "en",
      });
    },
    [chatMutation, conversationId, locale],
  );

  const examples = [t("example1"), t("example2"), t("example3")];

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 sm:px-6 sm:py-10">
      {/* Hero */}
      <section className="mb-8 text-center">
        <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-bd-green-200 bg-bd-green-50 px-4 py-1.5 text-sm text-bd-green-700">
          <span className="h-2 w-2 rounded-full bg-bd-green-500" aria-hidden="true" />
          {tCommon("verified")}
        </div>
        <h1 className="text-2xl font-bold text-gray-900 sm:text-3xl md:text-4xl">
          {t("heroTitle")}
        </h1>
        <p className="mx-auto mt-3 max-w-2xl text-sm text-gray-600 sm:text-base">
          {t("heroSubtitle")}
        </p>
      </section>

      {/* Chat area */}
      <section
        className="mb-8 flex min-h-[400px] flex-col rounded-2xl border border-gray-200 bg-white p-4 shadow-sm sm:min-h-[480px] sm:p-6"
        aria-label={tChat("title")}
      >
        <ChatThread
          messages={messages}
          isLoading={chatMutation.isPending}
          fallbackMode={fallbackMode}
        />

        {error && (
          <div className="mb-3 rounded-lg border border-bd-red-200 bg-bd-red-50 px-4 py-2 text-sm text-bd-red-700" role="alert">
            {error}
            <button
              type="button"
              onClick={() => setError(null)}
              className="ml-2 underline"
            >
              {tCommon("close")}
            </button>
          </div>
        )}

        <div className="mt-auto pt-4">
          <ChatInput
            onSend={handleSend}
            disabled={chatMutation.isPending}
            placeholder={t("placeholder")}
            autoFocus
          />
        </div>
      </section>

      {/* Example prompts */}
      <section className="mb-10">
        <p className="mb-3 text-sm font-medium text-gray-500">{t("examples")}</p>
        <div className="flex flex-wrap gap-2">
          {examples.map((ex) => (
            <button
              key={ex}
              type="button"
              onClick={() => handleSend(ex)}
              disabled={chatMutation.isPending}
              className="rounded-full border border-gray-200 bg-white px-4 py-2 text-sm text-gray-700 transition-colors hover:border-bd-green-300 hover:bg-bd-green-50 hover:text-bd-green-700 disabled:opacity-50"
            >
              {ex}
            </button>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="grid gap-4 sm:grid-cols-3">
        {[
          { title: t("feature1Title"), desc: t("feature1Desc"), icon: "📋" },
          { title: t("feature2Title"), desc: t("feature2Desc"), icon: "🌐" },
          { title: t("feature3Title"), desc: t("feature3Desc"), icon: "✓" },
        ].map((f) => (
          <div
            key={f.title}
            className="rounded-xl border border-gray-200 bg-white p-5"
          >
            <span className="text-2xl" aria-hidden="true">
              {f.icon}
            </span>
            <h3 className="mt-2 font-semibold text-gray-900">{f.title}</h3>
            <p className="mt-1 text-sm text-gray-600">{f.desc}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
