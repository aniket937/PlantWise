import { LoaderCircle } from "lucide-react";

export default function Loading() {
  return (
    <div className="mx-auto flex max-w-6xl items-center gap-3 px-4 py-24 sm:px-6">
      <LoaderCircle className="size-5 animate-spin text-primary" aria-hidden="true" />
      <p role="status" className="text-sm text-muted">
        Loading…
      </p>
    </div>
  );
}
