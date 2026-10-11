"use client";

import { Bot, Eraser, LoaderCircle, Send, Sparkles, User } from "lucide-react";
import { useEffect, useId, useRef, useState } from "react";

import { askAssistant } from "@/app/actions";
import type { AssistantStatusResponse, PlantSummary } from "@/types/api";

interface ChatEntry {
  role: "user" | "assistant";
  content: string;
  /** Set when the assistant could not answer, so the reason stays visible. */
  failureReason?: string;
  model?: string;
  latencyMs?: number | null;
}

interface AssistantChatProps {
  status: AssistantStatusResponse;
  plants: Pick<PlantSummary, "slug" | "common_name" | "scientific_name">[];
  initialPlantSlug?: string;
}

const PROMPT_IDEAS = [
  "How do I start this from seed?",
  "What should I feed it and when?",
  "Which pests should I watch for?",
  "How do I know when it is ready to harvest?",
];

export function AssistantChat({ status, plants, initialPlantSlug }: AssistantChatProps) {
  const inputId = useId();
  const plantId = useId();
  const logRef = useRef<HTMLDivElement>(null);
  const [entries, setEntries] = useState<ChatEntry[]>([]);
  const [draft, setDraft] = useState("");
  const [plantSlug, setPlantSlug] = useState(initialPlantSlug ?? "");
  const [busy, setBusy] = useState(false);
  const [transportError, setTransportError] = useState<string | null>(null);

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight });
  }, [entries]);

  const selectedPlant = plants.find((plant) => plant.slug === plantSlug);

  async function send(question: string) {
    const text = question.trim();
    if (!text || busy) return;

    setTransportError(null);
    const history: ChatEntry[] = [...entries, { role: "user", content: text }];
    setEntries(history);
    setDraft("");
    setBusy(true);

    const result = await askAssistant({
      messages: history.map((entry) => ({ role: entry.role, content: entry.content })),
      ...(plantSlug ? { plantSlug } : {}),
    });

    if (!result.ok) {
      setTransportError(result.message);
      setBusy(false);
      return;
    }

    const response = result.data;
    setEntries([
      ...history,
      response.available && response.reply
        ? {
            role: "assistant",
            content: response.reply,
            model: response.model,
            latencyMs: response.latency_ms,
          }
        : {
            role: "assistant",
            content: "",
            failureReason:
              response.unavailable_reason ??
              "The assistant could not produce an answer for that question.",
            model: response.model,
          },
    ]);
    setBusy(false);
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-[1fr_auto] sm:items-end">
        <div className="space-y-2">
          <label htmlFor={plantId} className="block text-sm font-medium text-foreground">
            Plant context for this conversation
          </label>
          <select
            id={plantId}
            value={plantSlug}
            onChange={(event) => setPlantSlug(event.target.value)}
            className="w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-foreground"
          >
            <option value="">No specific plant</option>
            {plants.map((plant) => (
              <option key={plant.slug} value={plant.slug}>
                {plant.common_name} ({plant.scientific_name})
              </option>
            ))}
          </select>
        </div>

        {entries.length > 0 ? (
          <button
            type="button"
            onClick={() => {
              setEntries([]);
              setTransportError(null);
            }}
            className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-2.5 text-sm text-muted hover:bg-surface-2 hover:text-foreground"
          >
            <Eraser className="size-4" aria-hidden="true" />
            Clear conversation
          </button>
        ) : null}
      </div>

      {selectedPlant ? (
        <p className="rounded-lg border border-border bg-surface-2 px-3 py-2 text-xs text-muted">
          Answers will be grounded in the recorded profile for{" "}
          <span className="font-medium text-foreground">{selectedPlant.common_name}</span>.
        </p>
      ) : null}

      <div
        ref={logRef}
        role="log"
        aria-live="polite"
        aria-label="Conversation"
        className="max-h-[26rem] min-h-[12rem] space-y-4 overflow-y-auto rounded-xl border border-border bg-surface p-4"
      >
        {entries.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center py-8 text-center">
            <span className="flex size-11 items-center justify-center rounded-full bg-sage text-primary">
              <Sparkles className="size-5" aria-hidden="true" />
            </span>
            <p className="mt-3 text-sm font-medium text-foreground">
              Ask a growing question
            </p>
            <p className="mt-1 max-w-md text-sm leading-relaxed text-muted">
              Answers come from a hosted open-weight model served through OpenRouter. It can
              explain the recorded plant data but it does not decide suitability.
            </p>
            <ul className="mt-4 flex flex-wrap justify-center gap-2">
              {PROMPT_IDEAS.map((idea) => (
                <li key={idea}>
                  <button
                    type="button"
                    onClick={() => send(idea)}
                    className="rounded-full border border-border px-3 py-1.5 text-xs text-muted hover:bg-surface-2 hover:text-foreground"
                  >
                    {idea}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          entries.map((entry, index) => (
            <article
              key={`${entry.role}-${index}`}
              className={`flex gap-3 ${entry.role === "user" ? "justify-end" : ""}`}
            >
              {entry.role === "assistant" ? (
                <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-sage text-primary">
                  <Bot className="size-4" aria-hidden="true" />
                </span>
              ) : null}

              <div className={`max-w-[85%] ${entry.role === "user" ? "order-first" : ""}`}>
                <div
                  className={`rounded-xl px-4 py-3 text-sm leading-relaxed ${
                    entry.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "border border-border bg-surface-2 text-foreground"
                  }`}
                >
                  {entry.failureReason ? (
                    <div className="space-y-1">
                      <p className="font-medium">No answer was produced</p>
                      <p className="opacity-90">{entry.failureReason}</p>
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap">{entry.content}</p>
                  )}
                </div>

                {entry.role === "assistant" && entry.model && !entry.failureReason ? (
                  <p className="mt-1 text-xs text-muted">
                    {entry.model}
                    {entry.latencyMs ? ` · ${(entry.latencyMs / 1000).toFixed(1)}s` : ""}
                  </p>
                ) : null}
              </div>

              {entry.role === "user" ? (
                <span className="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full border border-border text-muted">
                  <User className="size-4" aria-hidden="true" />
                </span>
              ) : null}
            </article>
          ))
        )}

        {busy ? (
          <p className="flex items-center gap-2 text-sm text-muted">
            <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />
            Generating. A hosted model can take a little while.
          </p>
        ) : null}
      </div>

      {transportError ? (
        <p role="alert" className="rounded-lg border border-fail/35 bg-fail-soft px-4 py-3 text-sm text-fail">
          {transportError}
        </p>
      ) : null}

      <form
        onSubmit={(event) => {
          event.preventDefault();
          void send(draft);
        }}
        className="flex flex-col gap-2 sm:flex-row"
      >
        <label htmlFor={inputId} className="sr-only">
          Your question
        </label>
        <input
          id={inputId}
          type="text"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder={status.available ? "Ask about growing this plant…" : "The assistant is offline"}
          autoComplete="off"
          className="flex-1 rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-foreground placeholder:text-muted"
        />
        <button
          type="submit"
          disabled={busy || draft.trim() === ""}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary-hover disabled:opacity-60"
        >
          <Send className="size-4" aria-hidden="true" />
          Send
        </button>
      </form>

      <p className="text-xs leading-relaxed text-muted">{status.detail}</p>
    </div>
  );
}
