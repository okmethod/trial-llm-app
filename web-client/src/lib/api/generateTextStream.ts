import { fetchStreamApi } from "$lib/utils/request";
import { pathGenTextStream } from "$lib/api/paths";
import { buildChatFormData, buildChatRequestConfig } from "$lib/api/generateText";
import type { ChatEntry } from "$lib/types/chat";

async function* generateTextStream(
  fetchFunction: typeof fetch,
  prompt: string,
  image?: File,
  chatHistory?: ChatEntry[],
): AsyncGenerator<string, void, unknown> {
  const url = pathGenTextStream;
  const formData = buildChatFormData(prompt, image, chatHistory);
  const requestConfig = buildChatRequestConfig(formData, "text/plain");
  const stream = await fetchStreamApi(fetchFunction, url, requestConfig);
  const reader = stream.getReader();
  const decoder = new TextDecoder();

  let streamDone = false;
  let decodedText = "";
  while (!streamDone) {
    const { value: binaryChunk, done: readerDone } = await reader.read();
    streamDone = readerDone;
    if (binaryChunk) {
      decodedText += decoder.decode(binaryChunk, { stream: !streamDone });
      yield decodedText;
      decodedText = "";
    }
  }
}

export default generateTextStream;
