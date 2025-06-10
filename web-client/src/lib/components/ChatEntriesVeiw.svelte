<script lang="ts">
  import type { ChatEntry } from "$lib/types/chat";

  export let initialMessage: string = "チャットを始めましょう。";
  export let chatEntries: ChatEntry[] = [];
  export let isProcessing: boolean = false;
</script>

<div class="size-full border rounded p-4 flex flex-col space-y-2 overflow-y-auto">
  {#if chatEntries.length === 0}
    <div class="text-gray-400">{initialMessage}</div>
  {/if}
  {#each chatEntries as msg, index (index)}
    <div class:self-end={msg.role === "human"} class:self-start={msg.role === "ai"}>
      <span class="font-bold">{msg.role === "human" ? "You" : "Ai"}:</span>
      <div class="rounded bg-primary-900 p-2 min-w-lg max-w-[80%] border">
        <span class="text-primary-100">{msg.content.text}</span>
        {#if isProcessing && msg.role === "ai" && index === chatEntries.length - 1 && !msg.content.text}
          <span class="text-gray-400 ml-2">応答中...</span>
        {/if}
        {#if msg.content.image}
          <div class="mt-1 flex justify-center">
            <img src={msg.content.image.url} alt="UploadedImage" class="w-40 rounded border" />
          </div>
        {/if}
      </div>
    </div>
  {/each}
</div>
