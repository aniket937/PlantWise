import type { ReactNode } from "react";

interface SectionHeadingProps {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
  /** Heading level, so the outline stays correct on every page. */
  as?: "h1" | "h2" | "h3";
  id?: string;
}

export function SectionHeading({
  eyebrow,
  title,
  description,
  action,
  as: Tag = "h2",
  id,
}: SectionHeadingProps) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-4">
      <div className="max-w-2xl">
        {eyebrow ? (
          <p className="text-xs font-semibold uppercase tracking-wide text-accent">
            {eyebrow}
          </p>
        ) : null}
        <Tag
          id={id}
          className="mt-1 text-xl font-semibold tracking-tight text-foreground sm:text-2xl"
        >
          {title}
        </Tag>
        {description ? (
          <p className="mt-2 text-sm leading-relaxed text-muted">{description}</p>
        ) : null}
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </div>
  );
}
