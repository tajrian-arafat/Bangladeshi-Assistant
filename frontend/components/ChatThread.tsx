"use client";

import { useRef, useEffect } from "react";
import type { ConversationMessage } from "@/types/api";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { CitationCard } from "./CitationCard";
import { ChecklistView } from "./ChecklistView";
import { ProcedureSteps } from "./ProcedureSteps";
import { ConflictWarning } from "./ConflictWarning";
import { useTranslations } from "next-intl";

interface ChatThreadProps {
  messages: ConversationMessage[];
  isLoading?: boolean;
  fallbackMode?: boolean;
}

function UserBubble({ content }: { content: string }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[85%] rounded-2xl rounded-br-sm bg-bd-green-500 px-4 py-3 text-sm text-white sm:max-w-[70%]">
        <p className="whitespace-pre-wrap break-words">{content}</p>
      </div>
    </div>
  );
}

function AssistantBubble({ message }: { message: ConversationMessage }) {
  const t = useTranslations("chat");

  return (
    <div className="flex justify-start">
      <div className="max-w-[95%] space-y-4 sm:max-w-[85%]">
        <div className="rounded-2xl rounded-bl-sm border border-gray-200 bg-white px-4 py-3 shadow-sm">
          {message.confidence && (
            <div className="mb-3">
              <ConfidenceBadge level={message.confidence} size="sm" />
            </div>
          )}

          <p className="whitespace-pre-wrap break-words text-sm text-gray-800">
            {message.content}
          </p>

          {message.answer?.warnings && message.answer.warnings.length > 0 && (
            <div className="mt-3">
              <ConflictWarning warnings={message.answer.warnings} />
            </div>
          )}

          {message.answer?.fees && message.answer.fees.length > 0 && (
            <div className="mt-4">
              <h4 className="mb-2 text-sm font-semibold text-gray-900">{t("fees")}</h4>
              <ul className="space-y-1">
                {message.answer.fees.map((fee, i) => (
                  <li key={i} className="text-sm text-gray-700">
                    {fee.label ? `${fee.label}: ` : ""}
                    <span className="font-medium">
                      {fee.amount} {fee.currency}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {message.answer?.checklist && message.answer.checklist.length > 0 && (
            <div className="mt-4 border-t border-gray-100 pt-4">
              <ChecklistView items={message.answer.checklist} />
            </div>
          )}

          {message.answer?.steps && message.answer.steps.length > 0 && (
            <div className="mt-4 border-t border-gray-100 pt-4">
              <ProcedureSteps steps={message.answer.steps} />
            </div>
          )}
        </div>

        {message.citations && message.citations.length > 0 && (
          <div>
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
              {t("citations")}
            </h4>
            <div className="space-y-2">
              {message.citations.map((citation, i) => (
                <CitationCard key={citation.evidence_id} citation={citation} index={i} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function LoadingBubble() {
  const t = useTranslations("chat");

  return (
    <div className="flex justify-start" role="status" aria-live="polite">
      <div className="rounded-2xl rounded-bl-sm border border-gray-200 bg-white px-4 py-3 shadow-sm">
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <span className="flex gap-1" aria-hidden="true">
            <span className="h-2 w-2 animate-bounce rounded-full bg-bd-green-400 [animation-delay:-0.3s]" />
            <span className="h-2 w-2 animate-bounce rounded-full bg-bd-green-400 [animation-delay:-0.15s]" />
            <span className="h-2 w-2 animate-bounce rounded-full bg-bd-green-400" />
          </span>
          {t("thinking")}
        </div>
      </div>
    </div>
  );
}

export function ChatThread({ messages, isLoading, fallbackMode }: ChatThreadProps) {
  const t = useTranslations("chat");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="flex flex-1 flex-col">
      {fallbackMode && (
        <div
          className="mb-4 rounded-lg border border-amber-300 bg-amber-50 px-4 py-2 text-sm text-amber-800"
          role="alert"
        >
          {t("limitedMode")}
        </div>
      )}

      <div className="flex-1 space-y-4 overflow-y-auto px-1 py-2">
        {messages.length === 0 && !isLoading && (
          <p className="py-8 text-center text-sm text-gray-400" role="status">
            {t("inputPlaceholder")}
          </p>
        )}

        {messages.map((msg) =>
          msg.role === "user" ? (
            <UserBubble key={msg.id} content={msg.content} />
          ) : (
            <AssistantBubble key={msg.id} message={msg} />
          ),
        )}

        {isLoading && <LoadingBubble />}
        <div ref={bottomRef} aria-hidden="true" />
      </div>
    </div>
  );
}
