import asyncio
import base64

from fastapi import UploadFile

from src.schemas.message import MessageEntryWithImageKey, MessageEntryWithImageUri


def image_file_to_data_uri(image: UploadFile) -> str:
    image_bytes = image.file.read() if hasattr(image, "file") else asyncio.run(image.read())
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{image.content_type};base64,{image_b64}"


def attach_image_uris_to_entries(
    entries: list[MessageEntryWithImageKey], images: list[UploadFile]
) -> list[MessageEntryWithImageUri]:
    image_map = {f.filename: f for f in images} if images else {}
    return [
        MessageEntryWithImageUri(
            role=entry.role,
            text=entry.text,
            image_uri=image_file_to_data_uri(image_map[entry.image_key])
            if entry.image_key and entry.image_key in image_map
            else None,
        )
        for entry in entries
    ]
