import Link from "next/link";
import { ArrowRight, Bot, ShieldCheck, Sparkles, TriangleAlert } from "lucide-react";

import { AssistantChat } from "@/components/assistant-chat";
import { Notice } from "@/components/feedback";
import { getAssistantStatus, getPlants } from "@/lib/api";

export const metadata = {
  title: "Growing assistant",
  description:
    "Ask growing questions answered by a hosted open-weight model grounded in the PlantWise plant profiles.",
};

interface AssistantPageProps {
  searchParams: Promise<{ plant?: string }>;
}

const SETUP_STEPS = [
  {
    command: "openrouter.ai/settings/keys",
    detail:
      "Create an account and generate an API key. Free open-weight models need no upfront credit, but free-tier requests are rate-limited per day.",
  },
  {
    command: "OPENROUTER_API_KEY=sk-or-...",
    detail:
      "Put the key in backend/.env. It is git-ignored and stays on the server — it never reaches the browser.",
  },
  {
    command: "OPENROUTER_MODEL=google/gemma-4-26b-a4b-it:free",
    detail:
      "The default is a free Google Gemma 4 model. Browse openrouter.ai/models to pick another free open-weight model.",
  },
] as const;

export default async function AssistantPage({ searchParams }: AssistantPageProps) {
  const params = await searchParams;
  const [status, plants] = await Promise.all([
    getAssistantStatus(),
    getPlants({ limit: 100 }),
  ]);

  const selectedPlant = params.plant;
  const plantOptions = plants.ok
    ? plants.data.items.map((plant) => ({
        slug: plant.slug,
        common_name: plant.common_name,
        scientific_name: plant.scientific_name,
      }))
    : [];

  const initialPlantSlug = plantOptions.some((plant) => plant.slug === selectedPlant)
    ? selectedPlant
    : undefined;

  const statusData = status.ok
    ? status.data
    : {
        available: false,
        model: "not configured",
        detail: status.message,
        checked_at: new Date().toISOString(),
        base_url_configured: false,
      };

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <header className="max-w-2xl">
        <p className="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-accent">
          <Bot className="size-3.5" aria-hidden="true" />
          AI assistant
        </p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight text-foreground">
          Growing assistant
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-muted">
          Ask about sowing, feeding, pruning, pests or harvest timing. A hosted
          open-weight model answers through OpenRouter and works from the same
          recorded profiles the rest of the site uses.
        </p>
      </header>

      <div className="mt-6 flex flex-wrap items-center gap-2 text-xs">
        {statusData.available ? (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-pass/35 bg-pass-soft px-3 py-1 font-medium text-pass">
            <Sparkles className="size-3.5" aria-hidden="true" />
            Ready · {statusData.model}
          </span>
        ) : (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-caution/35 bg-caution-soft px-3 py-1 font-medium text-caution">
            <TriangleAlert className="size-3.5" aria-hidden="true" />
            Unavailable · {statusData.model}
          </span>
        )}
        <span className="text-muted">
          Last checked {new Date(statusData.checked_at).toLocaleTimeString()}
        </span>
      </div>

      {!statusData.available ? (
        <div className="mt-6 space-y-4">
          <Notice tone="warning" title="The hosted assistant is offline right now">
            {statusData.detail} Everything else on the site keeps working without it: the
            suitability engine never calls a language model.
          </Notice>

          <div className="rounded-xl border border-border bg-surface p-5">
            <h2 className="text-sm font-semibold text-foreground">To enable the assistant</h2>
            <ol className="mt-3 space-y-3">
              {SETUP_STEPS.map((step, index) => (
                <li key={step.command} className="flex gap-3">
                  <span className="mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-md bg-sage text-xs font-semibold tabular-nums text-primary">
                    {index + 1}
                  </span>
                  <div>
                    <code className="rounded bg-surface-2 px-2 py-0.5 text-xs text-foreground">
                      {step.command}
                    </code>
                    <p className="mt-1 text-sm leading-relaxed text-muted">{step.detail}</p>
                  </div>
                </li>
              ))}
            </ol>
            <p className="mt-4 border-t border-border pt-3 text-xs leading-relaxed text-muted">
              Then restart the backend so it picks up the changed settings. Questions and the
              selected plant profile are sent from the backend to OpenRouter, a third-party
              service; the suitability engine never sends your data to a model.
            </p>
          </div>
        </div>
      ) : null}

      <section className="mt-8 rounded-xl border border-border bg-surface p-5 shadow-[var(--shadow)] sm:p-6">
        <AssistantChat
          status={statusData}
          plants={plantOptions}
          initialPlantSlug={initialPlantSlug}
        />
      </section>

      <section className="mt-8 grid gap-4 sm:grid-cols-2">
        <div className="rounded-xl border border-border bg-surface-2 p-4">
          <p className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <ShieldCheck className="size-4 text-primary" aria-hidden="true" />
            The model explains, it does not decide
          </p>
          <p className="mt-1.5 text-sm leading-relaxed text-muted">
            Suitability verdicts come from a documented rule engine. The assistant can
            restate or discuss those results, but it cannot change one.
          </p>
        </div>
        <div className="rounded-xl border border-border bg-surface-2 p-4">
          <p className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <Sparkles className="size-4 text-accent" aria-hidden="true" />
            Check the result, not just the words
          </p>
          <p className="mt-1.5 text-sm leading-relaxed text-muted">
            Open-weight models can be confidently wrong. For anything that matters, run a
            site check and confirm with local growing advice.
          </p>
          <Link
            href="/location"
            className="mt-3 inline-flex items-center gap-1.5 text-sm font-medium text-primary hover:underline"
          >
            Run a site check
            <ArrowRight className="size-4" aria-hidden="true" />
          </Link>
        </div>
      </section>
    </div>
  );
}
