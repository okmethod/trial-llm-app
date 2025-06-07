<script lang="ts">
  import { FileUpload } from "@skeletonlabs/skeleton-svelte";
  import type { FileChangeDetails } from "@zag-js/file-upload";
  import Icon from "@iconify/svelte";
  import generateText from "$lib/api/generateText";
  import { showErrorToast } from "$lib/utils/toaster";

  let input = "";
  let messages: { role: "user" | "assistant"; content: string }[] = [];
  let isProcessing = false;

  let uploadedImage: File | null = null;
  let uploadedImageUrl: string | null = null;
  function handleFileChange(details: FileChangeDetails) {
    uploadedImage = details.acceptedFiles[0];
    if (uploadedImage) {
      const reader = new FileReader();
      reader.onload = (e) => {
        uploadedImageUrl = e.target?.result as string;
      };
      reader.readAsDataURL(uploadedImage);
    } else {
      uploadedImageUrl = null;
    }
  }

  function removeImage() {
    uploadedImage = null;
    uploadedImageUrl = null;
  }

  async function sendMessage() {
    if (!input.trim()) return;
    messages = [...messages, { role: "user", content: input }];
    isProcessing = true;
    try {
      const answer = await generateText(fetch, input, uploadedImage ?? undefined);
      messages = [...messages, { role: "assistant", content: answer }];
    } catch (e) {
      showErrorToast("エラーが発生しました");
    }
    input = "";
    removeImage();
    isProcessing = false;
  }
</script>

<div class="flex flex-col items-center justify-center p-4 space-y-4 max-w-4xl mx-auto">
  <h2 class="h2">Dialog Chat</h2>
  <div class="w-full border rounded p-4 bg-surface-100-900 h-[400px] flex flex-col space-y-2 overflow-y-auto">
    {#if messages.length === 0}
      <div class="text-gray-400">チャットを始めましょう。</div>
    {/if}
    {#each messages as msg}
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
    <div class="flex items-center justify-center size-16">
      {#if !uploadedImageUrl}
        {#key uploadedImageUrl}
          <FileUpload
            name="image"
            accept="image/*"
            maxFiles={1}
            label=""
            onFileChange={handleFileChange}
            onFileReject={console.error}
            interfaceClasses="size-full"
            interfacePadding="p-5"
            filesListClasses="hidden"
            fileClasses="hidden"
            fileName="hidden"
            fileSize="hidden"
          >
            {#snippet iconInterface()}<Icon icon="mdi:image-plus" class="size-6" />{/snippet}
          </FileUpload>
        {/key}
      {:else}
        <div class="flex justify-center relative">
          <img src={uploadedImageUrl} alt="previewImage" class="size-full rounded border" />
          <button
            type="button"
            class="absolute top-0 right-0 bg-opacity-70 rounded-full"
            on:click={removeImage}
            aria-label="画像を削除"
          >
            <Icon icon="mdi:close-circle" class="size-4" />
          </button>
        </div>
      {/if}
    </div>
    <button type="submit" class="btn preset-filled-primary-500 rounded-lg" disabled={isProcessing || !input.trim()}>
      送信
    </button>
  </form>
</div>
