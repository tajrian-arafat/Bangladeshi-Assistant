"use client";

import { use, useState, useCallback } from "react";
import { useTranslations, useLocale } from "next-intl";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Link } from "@/i18n/routing";
import { ChatThread } from "@/components/ChatThread";
import { ChatInput } from "@/components/ChatInput";
import { api, ApiClientError } from "@/lib/api";
import type { ConversationMessage } from "@/types/api";

interface ChatPageProps {
  params: Promise<{ id: string }>;
}

export default function ChatPage({ params }: ChatPageProps) {
  const { id } = use(params);
  const t = useTranslations("chat");
  const tCommon = useTranslations("common");
  const locale = useLocale();

  const [localMessages, setLocalMessages] = useState<ConversationMessage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [fallbackMode, setFallbackMode] = useState(false);

  const { data: conversation, isLoading, isError } = useQuery({
    queryKey: ["conversation", id],
    queryFn: () => api.getConversation(id),
    retry: false,
  });

  const chatMutation = useMutation({
    mutationFn: api.chat,
    onSuccess: (data) => {
      setFallbackMode(data.metadata?.fallback_mode ?? false);
      const assistantMsg: ConversationMessage = {
        id: data.message_id,
        role: "assistant",
        content: data.answer.summary,
        confidence: data.confidence,
        answer: data.answer,
        citations: data.citations,
      };
      setLocalMessages((prev) => [...prev, assistantMsg]);
    },
    onError: (err: Error) => {
      setError(err instanceof ApiClientError ? err.message : tCommon("error"));
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
      setLocalMessages((prev) => [...prev, userMsg]);
      chatMutation.mutate({
        message,
        conversation_id: id,
        language_preference: locale === "bn" ? "bn" : "en",
      });
    },
    [chatMutation, id, locale],
  );

  const allMessages = [
    ...(conversation?.messages ?? []),
    ...localMessages,
  ];

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center">
        <p className="text-sm text-gray-500" role="status">
          {tCommon("loading")}
        </p>
      </div>
    );
  }

  if (isError && localMessages.length === 0) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 text-center">
        <p className="text-gray-600">{t("noEvidence")}</p>
        <Link
          href="/"
          className="mt-4 inline-block text-sm font-medium text-bd-green-600 hover:underline"
        >
          {t("newChat")}
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-8rem)] max-w-4xl flex-col px-4 py-4 sm:px-6">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-lg font-semibold text-gray-900">{t("title")}</h1>
        <Link
          href="/"
          className="text-sm font-medium text-bd-green-600 hover:underline"
        >
          {t("newChat")}
        </Link>
      </div>

      <div className="flex flex-1 flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white p-4 shadow-sm sm:p-6">
        <ChatThread
          messages={allMessages}
          isLoading={chatMutation.isPending}
          fallbackMode={fallbackMode}
        />

        {error && (
          <div className="mb-3 rounded-lg border border-bd-red-200 bg-bd-red-50 px-4 py-2 text-sm text-bd-red-700" role="alert">
            {error}
          </div>
        )}

        <div className="mt-auto pt-4">
          <ChatInput onSend={handleSend} disabled={chatMutation.isPending} />
        </div>
      </div>
    </div>
  );
}
