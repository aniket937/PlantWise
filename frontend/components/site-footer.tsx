import Link from "next/link";
import { Leaf } from "lucide-react";

const DATA_SOURCES = [
  {
    href: "https://ecocrop.apps.fao.org/ecocrop/srv/en/home",
    label: "FAO EcoCrop",
  },
  { href: "https://plants.usda.gov/", label: "USDA PLANTS" },
  { href: "https://www.rhs.org.uk/", label: "RHS growing guides" },
  { href: "https://www.fao.org/faostat/en/#data/QCL", label: "FAOSTAT" },
  { href: "https://www.feedipedia.org/", label: "Feedipedia" },
] as const;

const PROVIDERS = [
  {
    href: "https://open-meteo.com/en/docs/historical-weather-api",
    label: "Open-Meteo historical archive (ERA5)",
  },
  {
    href: "https://open-meteo.com/en/docs/geocoding-api",
    label: "Open-Meteo geocoding",
  },
  {
    href: "https://www.openstreetmap.org/copyright",
    label: "OpenStreetMap contributors",
  },
  {
    href: "https://openrouter.ai/",
    label: "OpenRouter, hosting the open-weight Gemma model",
  },
] as const;

export function SiteFooter() {
  return (
    <footer className="mt-16 border-t border-border bg-surface">
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <div className="grid gap-8 md:grid-cols-3">
          <div>
            <div className="flex items-center gap-2 font-semibold text-foreground">
              <span className="flex size-7 items-center justify-center rounded-md bg-primary text-primary-foreground">
                <Leaf className="size-4" aria-hidden="true" />
              </span>
              PlantWise AI
            </div>
            <p className="mt-3 max-w-xs text-sm leading-relaxed text-muted">
              Plant discovery and location-based growing suitability. Verdicts come from a
              documented comparison of crop requirements against long-term climate
              normals, never from a language model.
            </p>
          </div>

          <nav aria-label="Footer">
            <h2 className="text-sm font-semibold text-foreground">Explore</h2>
            <ul className="mt-3 space-y-2 text-sm">
              {[
                { href: "/explore", label: "Explore plants" },
                { href: "/location", label: "Check a location" },
                { href: "/regions", label: "Growing regions" },
                { href: "/assistant", label: "AI assistant" },
              ].map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-muted underline-offset-4 hover:text-foreground hover:underline"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>

          <div>
            <h2 className="text-sm font-semibold text-foreground">Data and attribution</h2>
            <ul className="mt-3 space-y-2 text-sm">
              {DATA_SOURCES.map((source) => (
                <li key={source.href}>
                  <a
                    href={source.href}
                    className="text-muted underline-offset-4 hover:text-foreground hover:underline"
                    rel="noreferrer noopener"
                    target="_blank"
                  >
                    {source.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-8 border-t border-border pt-6">
          <h2 className="text-sm font-semibold text-foreground">Services used</h2>
          <ul className="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-sm">
            {PROVIDERS.map((provider) => (
              <li key={provider.href}>
                <a
                  href={provider.href}
                  className="text-muted underline-offset-4 hover:text-foreground hover:underline"
                  rel="noreferrer noopener"
                  target="_blank"
                >
                  {provider.label}
                </a>
              </li>
            ))}
          </ul>
          <p className="mt-6 text-xs leading-relaxed text-muted">
            This tool supports planning, not a guarantee. Crop requirement ranges are
            indicative agronomic envelopes from published references, and they are not
            cultivar-specific. Confirm important decisions locally before committing land,
            water or money.
          </p>
        </div>
      </div>
    </footer>
  );
}
