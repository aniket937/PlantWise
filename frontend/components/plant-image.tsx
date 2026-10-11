import Image from "next/image";
import { Sprout } from "lucide-react";

interface PlantImageProps {
  src: string | null;
  alt: string;
  /** Rendered as a CSS aspect ratio class, e.g. "aspect-[4/3]". */
  aspectClassName?: string;
  sizes: string;
  preload?: boolean;
}

/**
 * Plant photography with an honest placeholder.
 *
 * When a profile has no image the space is filled with a labelled panel rather
 * than a stock photo, so the absence is visible instead of papered over.
 */
export function PlantImage({
  src,
  alt,
  aspectClassName = "aspect-[4/3]",
  sizes,
  preload = false,
}: PlantImageProps) {
  if (!src) {
    return (
      <div
        className={`${aspectClassName} flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-border-strong bg-surface-2 text-muted`}
        role="img"
        aria-label={`No photograph available for ${alt}`}
      >
        <Sprout className="size-6" aria-hidden="true" />
        <span className="px-3 text-center text-xs">No photograph available</span>
      </div>
    );
  }

  return (
    <div className={`${aspectClassName} relative overflow-hidden rounded-lg bg-surface-2`}>
      <Image
        src={src}
        alt={alt}
        fill
        sizes={sizes}
        className="object-cover"
        preload={preload}
      />
    </div>
  );
}
