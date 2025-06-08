export function constructRequestInit(): RequestInit {
  const requestInit = {
    credentials: "same-origin",
  } as RequestInit;
  return requestInit;
}

export async function fetchApi(
  fetchFunction: typeof fetch,
  url: string,
  requestConfig: RequestInit,
): Promise<Response> {
  try {
    return await fetchFunction(url, requestConfig);
  } catch (e) {
    console.error("API error:", e);
    throw new Error(`Failed to fetch: ${requestConfig.method} ${url}`);
  }
}

export async function fetchStreamApi(
  fetchFunction: typeof fetch,
  url: string,
  requestConfig: RequestInit,
): Promise<ReadableStream<Uint8Array>> {
  try {
    const response = await fetchFunction(url, requestConfig);
    if (!response.body) throw new Error("No response body");
    return response.body;
  } catch (e) {
    console.error("Stream API error:", e);
    throw new Error(`Failed to fetch stream: ${requestConfig.method} ${url}`);
  }
}
