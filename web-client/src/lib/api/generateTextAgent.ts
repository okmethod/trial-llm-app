import { constructRequestInit, fetchApi } from "$lib/utils/request";
import { pathGenTextAgent } from "$lib/api/paths";
import type { ChatRole, ChatEntry } from "$lib/types/chat";

interface ResponseJson {
  message: string;
}

function extractHistoryEntries(chatHistory: ChatEntry[]): {
  role: ChatRole;
  text: string;
  image_key: null;
}[] {
  return chatHistory.map((entry) => ({
    role: entry.role,
    text: entry.content.text,
    image_key: null,
  }));
}

export async function generateTextAgent(
  fetchFunction: typeof fetch,
  prompt: string,
  chatHistory?: ChatEntry[],
): Promise<string> {
  const url = pathGenTextAgent;
  const formData = new FormData();
  formData.append("prompt", prompt);
  if (chatHistory && chatHistory.length > 0) {
    const entries = extractHistoryEntries(chatHistory);
    formData.append("history_json", JSON.stringify(entries));
  }
  const requestInit = constructRequestInit();
  const requestConfig: RequestInit = {
    ...requestInit,
    method: "POST",
    headers: {
      ...requestInit.headers,
      Accept: "application/json",
      // Content-Typeは自動設定
    },
    body: formData,
  };
  const response = await fetchApi(fetchFunction, url, requestConfig);
  const { message } = (await response.json()) as ResponseJson;
  return message;
}

export default generateTextAgent;
