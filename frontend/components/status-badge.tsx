import { CircleAlert, CircleCheck, CircleHelp, TriangleAlert } from "lucide-react";

import { CRITERION_STATUS_LABEL, STATUS_TONE } from "@/lib/format";
import type { CriterionStatus } from "@/types/api";

const ICON: Record<CriterionStatus, typeof CircleCheck> = {
  pass: CircleCheck,
  caution: TriangleAlert,
  fail: CircleAlert,
  unknown: CircleHelp,
};

interface StatusBadgeProps {
  status: CriterionStatus;
  /** Override the default wording, e.g. "Met" inside a dense table. */
  label?: string;
  className?: string;
}

export function StatusBadge({ status, label, className = "" }: StatusBadgeProps) {
  const Icon = ICON[status];
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${STATUS_TONE[status]} ${className}`}
    >
      <Icon className="size-3.5" aria-hidden="true" />
      {label ?? CRITERION_STATUS_LABEL[status]}
    </span>
  );
}
