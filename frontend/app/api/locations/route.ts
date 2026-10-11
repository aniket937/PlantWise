import { NextResponse } from "next/server";

import { searchLocations } from "@/lib/api";

/**
 * Server-side proxy for place search.
 *
 * The browser never learns the backend URL, and the geocoding provider stays
 * swappable without touching client code. A provider outage returns 200 with an
 * `unavailable_reason` so the UI can show a soft state instead of an error.
 */
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = (searchParams.get("q") ?? "").trim();
  const limit = Math.min(Math.max(Number(searchParams.get("limit") ?? 6) || 6, 1), 20);

  if (query.length < 2) {
    return NextResponse.json(
      {
        query,
        provider: "",
        results: [],
        unavailable_reason: "Type at least two characters to search for a place.",
      },
      { status: 200 },
    );
  }

  const result = await searchLocations(query, limit);
  if (!result.ok) {
    return NextResponse.json(
      {
        query,
        provider: "",
        results: [],
        unavailable_reason:
          result.code === "unreachable" || result.code === "timeout"
            ? "Place search is unavailable right now. You can enter coordinates directly instead."
            : result.message,
      },
      { status: 200 },
    );
  }

  return NextResponse.json(result.data, { status: 200 });
}
