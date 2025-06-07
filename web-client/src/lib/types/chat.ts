import type { ImageWithPreview } from "$lib/types/image";

export type ChatRole = "human" | "ai";

export interface ChatEntry {
  role: ChatRole;
  content: {
    text: string;
    image?: ImageWithPreview;
  };
}
