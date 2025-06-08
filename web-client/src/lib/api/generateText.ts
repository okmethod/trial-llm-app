import { constructRequestInit, fetchApi } from "$lib/utils/request";
import { pathGenText } from "$lib/api/paths";
import type { ChatRole, ChatEntry } from "$lib/types/chat";

interface ResponseJson {
  message: string;
}

interface MessageEntryWithImageKey {
  role: ChatRole;
  text: string;
  image_key: string | null;
}

function extractHistoryEntriesAndImages(chatHistory: ChatEntry[]): {
  entries: MessageEntryWithImageKey[];
  images: { file: File; filename: string }[];
} {
  const images: { file: File; filename: string }[] = [];
  const entries: MessageEntryWithImageKey[] = chatHistory.map((entry) => {
    let image_key: string | undefined = undefined;
    if (entry.content.image) {
      image_key = `image_${images.length}`;
      images.push({ file: entry.content.image.file, filename: image_key });
    }
    return {
      role: entry.role,
      text: entry.content.text,
      image_key: image_key ?? null,
    };
  });
  return { entries, images };
}

function buildChatFormData(prompt: string, image?: File, chatHistory?: ChatEntry[]): FormData {
  const formData = new FormData();
  formData.append("prompt", prompt);
  if (image) formData.append("image", image);
  if (chatHistory && chatHistory.length > 0) {
    const { entries, images } = extractHistoryEntriesAndImages(chatHistory);
    formData.append("history_json", JSON.stringify(entries));
    images.forEach(({ file, filename }) => {
      formData.append("history_images", file, filename);
    });
  }
  return formData;
}

function buildChatRequestConfig(formData: FormData, accept: string): RequestInit {
  const requestInit = constructRequestInit();
  return {
    ...requestInit,
    method: "POST",
    headers: {
      ...requestInit.headers,
      Accept: accept,
      // Content-Type は自動設定
    },
    body: formData,
  };
}

async function generateText(
  fetchFunction: typeof fetch,
  prompt: string,
  image?: File,
  chatHistory?: ChatEntry[],
): Promise<string> {
  const url = pathGenText;
  const formData = buildChatFormData(prompt, image, chatHistory);
  const requestConfig = buildChatRequestConfig(formData, "application/json");
  const response = await fetchApi(fetchFunction, url, requestConfig);
  const { message } = (await response.json()) as ResponseJson;
  return message;
}

export default generateText;
