<script lang="ts">
  import ImageUpload from "$lib/components/buttons/ImageUpload.svelte";
  import generateText from "$lib/api/generateText";
  import type { ImageWithPreview } from "$lib/types/image";
  import { showErrorToast } from "$lib/utils/toaster";

  interface ChatEntry {
    role: "user" | "assistant";
    content: {
      text: string;
      image?: ImageWithPreview;
    };
  }

  let chatEntries: ChatEntry[] = [];

  let currentInputText = "";
  let currentImage: ImageWithPreview | null = null;
  let isProcessing = false;

  async function sendMessage() {
    if (!currentInputText.trim()) return;
    chatEntries = [
      ...chatEntries,
      {
        role: "user",
        content: {
          text: currentInputText,
          ...(currentImage ? { image: currentImage } : {}),
        },
      },
    ];
    isProcessing = true;
    try {
      const answer = await generateText(fetch, currentInputText, currentImage?.file ?? undefined);
      chatEntries = [...chatEntries, { role: "assistant", content: { text: answer } }];
    } catch {
      showErrorToast("エラーが発生しました");
    }
    currentInputText = "";
    currentImage = null;
    isProcessing = false;
  }
</script>

<div class="flex flex-col items-center justify-center p-4 space-y-4 max-w-4xl mx-auto">
  <h2 class="h2">Dialog Chat</h2>
  <div class="w-full border rounded p-4 bg-surface-100-900 h-[400px] flex flex-col space-y-2 overflow-y-auto">
    {#if chatEntries.length === 0}
      <div class="text-gray-400">チャットを始めましょう。</div>
    {/if}
    {#each chatEntries as msg, index (index)}
      <div class:self-end={msg.role === "user"} class:self-start={msg.role === "assistant"}>
        <span class="font-bold">{msg.role === "user" ? "You" : "Ai"}:</span>
        <div class="rounded bg-primary-900 p-2 min-w-lg max-w-[80%] border">
          <span>{msg.content.text}</span>
          {#if msg.content.image}
            <div class="mt-2 flex justify-center">
              <img src={msg.content.image.url} alt="UploadedImage" class="w-32 rounded border" />
            </div>
          {/if}
        </div>
      </div>
    {/each}
    {#if isProcessing}
      <div class="text-gray-400">応答中...</div>
    {/if}
  </div>
  <form class="w-full flex space-x-2" on:submit|preventDefault={sendMessage}>
    <label id="chat-label" for="chat-input" class="sr-only">チャット入力</label>
    <input
      class="flex-1 border rounded p-2 text-gray-900"
      type="text"
      id="chat-input"
      name="prompt"
      bind:value={currentInputText}
      placeholder="メッセージを入力"
      autocomplete="off"
      disabled={isProcessing}
    />
    <div class="size-16">
      <ImageUpload bind:uploadedImage={currentImage} />
    </div>
    <button
      type="submit"
      class="btn preset-filled-primary-500 rounded-lg"
      disabled={isProcessing || !currentInputText.trim()}
    >
      送信
    </button>
  </form>
</div>
