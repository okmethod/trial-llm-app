import { constructRequestInit, fetchApi } from "$lib/utils/request";
import { pathGenText } from "$lib/api/paths";

interface ResponseJson {
  message: string;
}

async function generateText(fetchFunction: typeof fetch, prompt: string): Promise<string> {
  const url = pathGenText;
  const requestInit = constructRequestInit();

  const formData = new FormData();
  formData.append("prompt", prompt);

  const requestConfig = {
    ...requestInit,
    method: "POST",
    headers: {
      Accept: "application/json",
    },
    body: formData,
  };
  const response = await fetchApi(fetchFunction, url, requestConfig);
  const { message } = (await response.json()) as ResponseJson;
  return message;
}

export default generateText;
