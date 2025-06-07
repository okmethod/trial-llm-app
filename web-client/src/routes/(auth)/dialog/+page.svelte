<script lang="ts">
  import ImageUpload from "$lib/components/buttons/ImageUpload.svelte";
  import generateText from "$lib/api/generateText";
  import type { ImageWithPreview } from "$lib/types/image";
  import { showErrorToast } from "$lib/utils/toaster";

  let messages: { role: "user" | "assistant"; content: string }[] = [];
  let isProcessing = false;

  let currentImage: ImageWithPreview | null = null;

  let input = "";
  async function sendMessage() {
    if (!input.trim()) return;
    messages = [...messages, { role: "user", content: input }];
    isProcessing = true;
    try {
      const answer = await generateText(fetch, input, currentImage?.file ?? undefined);
      messages = [...messages, { role: "assistant", content: answer }];
    } catch {
      showErrorToast("エラーが発生しました");
    }
    input = "";
    currentImage = null;
    isProcessing = false;
  }
</script>

<div class="flex flex-col items-center justify-center p-4 space-y-4 max-w-4xl mx-auto">
  <h2 class="h2">Dialog Chat</h2>
  <div class="w-full border rounded p-4 bg-surface-100-900 h-[400px] flex flex-col space-y-2 overflow-y-auto">
    {#if messages.length === 0}
      <div class="text-gray-400">チャットを始めましょう。</div>
    {/if}
    {#each messages as msg, index (index)}
      <div class:self-end={msg.role === "user"} class:self-start={msg.role === "assistant"}>
        <span class="font-bold">{msg.role === "user" ? "You" : "Ai"}:</span>
        <div class="rounded bg-primary-900 p-2 min-w-lg max-w-[80%] border">
          <span>{msg.content}</span>
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
      bind:value={input}
      placeholder="メッセージを入力"
      autocomplete="off"
      disabled={isProcessing}
    />
    <div class="size-16">
      <ImageUpload bind:uploadedImage={currentImage} />
    </div>
    <button type="submit" class="btn preset-filled-primary-500 rounded-lg" disabled={isProcessing || !input.trim()}>
      送信
    </button>
  </form>
</div>
