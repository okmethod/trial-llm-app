import { fetchApi } from "$lib/utils/request";
import { pathGenTextAgent } from "$lib/api/paths";
import { buildChatFormData, buildChatRequestConfig } from "$lib/api/generateText";
import type { ChatEntry } from "$lib/types/chat";
import type { SimpleMessageJson } from "$lib/types/response";

export async function generateTextAgent(
  fetchFunction: typeof fetch,
  prompt: string,
  image?: File,
  chatHistory?: ChatEntry[],
): Promise<string> {
  const url = pathGenTextAgent;
  const formData = buildChatFormData(prompt, image, chatHistory);
  const requestConfig = buildChatRequestConfig(formData, "application/json");
  const response = await fetchApi(fetchFunction, url, requestConfig);
  const { message } = (await response.json()) as SimpleMessageJson;
  return message;
}

export default generateTextAgent;
