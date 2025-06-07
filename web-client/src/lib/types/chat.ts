import type { ImageWithPreview } from "$lib/types/image";

export interface ChatEntry {
  role: "user" | "assistant";
  content: {
    text: string;
    image?: ImageWithPreview;
  };
}
