<script lang="ts">
  import { Switch } from "@skeletonlabs/skeleton-svelte";
  import Icon from "@iconify/svelte";
  import generateText from "$lib/api/generateText";
  import generateTextStream from "$lib/api/generateTextStream";
  import type { ChatEntry } from "$lib/types/chat";
  import type { ImageWithPreview } from "$lib/types/image";
  import ChatEntriesVeiw from "$lib/components/ChatEntriesVeiw.svelte";
  import ImageUpload from "$lib/components/buttons/ImageUpload.svelte";
  import { showErrorToast } from "$lib/utils/toaster";

  let chatEntries: ChatEntry[] = [];

  let currentInputText = "";
  let currentImage: ImageWithPreview | null = null;
  let isProcessing = false;

  async function handleSendMessage(aiHandler: (history: ChatEntry[], humanEntry: ChatEntry) => Promise<void>) {
    if (!currentInputText.trim()) return;
    isProcessing = true;

    const history = chatEntries;
    const humanEntry: ChatEntry = {
      role: "human",
      content: {
        text: currentInputText,
        ...(currentImage ? { image: currentImage } : {}),
      },
    };

    await aiHandler(history, humanEntry);

    currentInputText = "";
    currentImage = null;
    isProcessing = false;
  }

  async function sendMessage() {
    await handleSendMessage(async (history, humanEntry) => {
      chatEntries = [...chatEntries, humanEntry];
      try {
        const aiText = await generateText(fetch, currentInputText, currentImage?.file ?? undefined, history);
        const aiEntry: ChatEntry = {
          role: "ai",
          content: { text: aiText },
        };
        chatEntries = [...chatEntries, aiEntry];
      } catch {
        showErrorToast("エラーが発生しました");
      }
    });
  }

  async function sendMessageStream() {
    await handleSendMessage(async (history, humanEntry) => {
      const aiEntry: ChatEntry = { role: "ai", content: { text: "" } };
      chatEntries = [...chatEntries, humanEntry, aiEntry];
      const latestIndex = chatEntries.length - 1;
      try {
        let aiStreamText = "";
        for await (const chunk of generateTextStream(
          fetch,
          currentInputText,
          currentImage?.file ?? undefined,
          history,
        )) {
          aiStreamText += chunk;
          chatEntries[latestIndex] = { role: "ai", content: { text: aiStreamText } };
          chatEntries = [...chatEntries]; // Svelteの再描画用
        }
      } catch {
        showErrorToast("エラーが発生しました");
      }
    });
  }

  let useStream = false;
  function handleStreamModeChange(checked: boolean) {
    useStream = checked;
  }
</script>

<div class="flex flex-col items-center justify-center p-4 space-y-4 max-w-4xl mx-auto">
  <h2 class="h2">Dialog Chat</h2>
  <div class="flex items-center mb-2">
    <Switch name="stream-mode" checked={useStream} onCheckedChange={(e) => handleStreamModeChange(e.checked)}>
      {#snippet inactiveChild()}<Icon icon="mdi:play-circle-outline" class="size-4" />{/snippet}
      {#snippet activeChild()}<Icon icon="mdi:play-speed" class="size-4" />{/snippet}
    </Switch>
    <span class="ml-2 text-sm text-gray-500 w-30">mode: {useStream ? "stream" : "sync"}</span>
  </div>
  <div class="w-full h-[400px] bg-surface-100-900">
    <ChatEntriesVeiw {chatEntries} {isProcessing} />
  </div>
  <form
    class="w-full flex space-x-2"
    on:submit|preventDefault={() => (useStream ? sendMessageStream() : sendMessage())}
  >
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
