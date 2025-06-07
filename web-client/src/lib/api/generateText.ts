import { constructRequestInit, fetchApi } from "$lib/utils/request";
import { pathGenText } from "$lib/api/paths";

interface ResponseJson {
  message: string;
}

async function generateText(fetchFunction: typeof fetch, prompt: string, image?: File): Promise<string> {
  const url = pathGenText;
  const requestInit = constructRequestInit();

  const formData = new FormData();
  formData.append("prompt", prompt);
  if (image) {
    formData.append("image", image);
  }

  const requestConfig = {
    ...requestInit,
    method: "POST",
    headers: {
      ...requestInit.headers,
      Accept: "application/json",
      // Content-Type は自動設定
    },
    body: formData,
  };
  const response = await fetchApi(fetchFunction, url, requestConfig);
  const { message } = (await response.json()) as ResponseJson;
  return message;
}

export default generateText;
