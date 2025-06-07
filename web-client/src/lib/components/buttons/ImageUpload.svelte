<script lang="ts">
  import { FileUpload } from "@skeletonlabs/skeleton-svelte";
  import Icon from "@iconify/svelte";
  import type { FileChangeDetails } from "@zag-js/file-upload";
  import type { ImageWithPreview } from "$lib/types/image";

  export let uploadedImage: ImageWithPreview | null = null;

  function handleFileChange(details: FileChangeDetails) {
    const file = details.acceptedFiles[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        uploadedImage = {
          file: file,
          url: e.target?.result as string,
        };
      };
      reader.readAsDataURL(file);
    } else {
      uploadedImage = null;
    }
  }

  function removeImage() {
    uploadedImage = null;
  }
</script>

<div class="flex items-center justify-center">
  {#if !uploadedImage}
    {#key uploadedImage}
      <FileUpload
        name="image"
        accept="image/*"
        maxFiles={1}
        label=""
        onFileChange={handleFileChange}
        onFileReject={console.error}
        interfaceBorderColor="border-surface-100-900"
        interfaceRounded="rounded-lg"
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
      <img src={uploadedImage.url} alt="previewImage" class="size-full rounded border" />
      <button
        type="button"
        class="absolute top-0 right-0 bg-opacity-70 rounded-full text-gray-500"
        on:click={removeImage}
        aria-label="画像を削除"
      >
        <Icon icon="mdi:close-circle" class="size-4" />
      </button>
    </div>
  {/if}
</div>
