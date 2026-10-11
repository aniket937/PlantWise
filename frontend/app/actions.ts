"use server";

import { postAssistantChat, type ChatMessageInput } from "@/lib/api";
import type { AssistantChatResponse } from "@/types/api";

export interface AskAssistantInput {
  messages: ChatMessageInput[];
  plantSlug?: string;
  location?: {
    latitude: number;
    longitude: number;
    label?: string;
    country?: string;
    admin_area?: string;
  };
}

export type AskAssistantResult =
  | { ok: true; data: AssistantChatResponse }
  | { ok: false; message: string };

/**
 * Server action behind the assistant chat.
 *
 * The model runtime is optional. An unreachable backend becomes a normal result
 * with `ok: false`, which the UI renders as an explanatory state, so the chat
 * never silently does nothing.
 */
export async function askAssistant(
  input: AskAssistantInput,
): Promise<AskAssistantResult> {
  if (input.messages.length === 0) {
    return { ok: false, message: "Type a question before sending." };
  }

  const result = await postAssistantChat({
    messages: input.messages,
    plant_slug: input.plantSlug,
    ...(input.location ? { location: input.location } : {}),
  });

  if (!result.ok) {
    return { ok: false, message: result.message };
  }
  return { ok: true, data: result.data };
}
