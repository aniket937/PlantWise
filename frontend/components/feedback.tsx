import type { ReactNode } from "react";

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border-strong bg-surface px-6 py-12 text-center">
      <span className="flex size-11 items-center justify-center rounded-full bg-sage text-primary">
        {icon}
      </span>
      <h3 className="mt-4 text-base font-semibold text-foreground">{title}</h3>
      <p className="mt-2 max-w-md text-sm leading-relaxed text-muted">{description}</p>
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  );
}

interface NoticeProps {
  tone: "info" | "warning" | "error";
  title: string;
  children: ReactNode;
}

const NOTICE_TONE = {
  info: "border-border bg-surface-2 text-foreground",
  warning: "border-caution/35 bg-caution-soft text-caution",
  error: "border-fail/35 bg-fail-soft text-fail",
} as const;

/** An inline, non-fatal message. Used instead of a toast that can be missed. */
export function Notice({ tone, title, children }: NoticeProps) {
  const role = tone === "error" ? "alert" : "status";
  return (
    <div
      role={role}
      className={`rounded-lg border px-4 py-3 text-sm ${NOTICE_TONE[tone]}`}
    >
      <p className="font-medium">{title}</p>
      <div className="mt-1 leading-relaxed opacity-90">{children}</div>
    </div>
  );
}
