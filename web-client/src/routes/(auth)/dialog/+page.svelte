<script lang="ts">
  import generateText from "$lib/api/generateText";
  import type { ChatEntry } from "$lib/types/chat";
  import type { ImageWithPreview } from "$lib/types/image";
  import ChatEntriesVeiw from "$lib/components/ChatEntriesVeiw.svelte";
  import ImageUpload from "$lib/components/buttons/ImageUpload.svelte";
  import { showErrorToast } from "$lib/utils/toaster";

  let chatEntries: ChatEntry[] = [];

  let currentInputText = "";
  let currentImage: ImageWithPreview | null = null;
  let isProcessing = false;

  async function sendMessage() {
    if (!currentInputText.trim()) return;
    chatEntries = [
      ...chatEntries,
      {
        role: "human",
        content: {
          text: currentInputText,
          ...(currentImage ? { image: currentImage } : {}),
        },
      },
    ];
    isProcessing = true;
    try {
      const answer = await generateText(fetch, currentInputText, currentImage?.file ?? undefined);
      chatEntries = [...chatEntries, { role: "ai", content: { text: answer } }];
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
  <div class="w-full h-[400px] bg-surface-100-900">
    <ChatEntriesVeiw {chatEntries} {isProcessing} />
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
