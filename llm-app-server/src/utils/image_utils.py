import base64
from collections.abc import Callable
from typing import Any

from fastapi import UploadFile

from src.schemas.image import ImageBytes
from src.schemas.message import MessageEntryWithImageKey, MessageEntryWithImageUri


async def uploadfile_to_image_bytes(
    upload_file: UploadFile,
) -> ImageBytes:
    data = await upload_file.read()
    content_type = upload_file.content_type or "application/octet-stream"
    image_key = upload_file.filename if hasattr(upload_file, "filename") and upload_file.filename else "image_0"
    return ImageBytes(image_key=image_key, data=data, content_type=content_type)


def image_bytes_to_data_uri(image_bytes: bytes, content_type: str) -> str:
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{content_type};base64,{image_b64}"


def bytes_to_image_dict(
    image_bytes: bytes,
    content_type: str,
    image_dict_factory: Callable[[str], dict[str, Any]],
) -> dict[str, Any]:
    return image_dict_factory(image_bytes_to_data_uri(image_bytes, content_type))


def attach_image_uris_to_entries(
    entries: list[MessageEntryWithImageKey],
    images: list[ImageBytes],
) -> list[MessageEntryWithImageUri]:
    image_map = {img.image_key: img for img in images}
    return [
        MessageEntryWithImageUri(
            role=entry.role,
            text=entry.text,
            image_uri=image_bytes_to_data_uri(image_map[entry.image_key].data, image_map[entry.image_key].content_type)
            if entry.image_key and entry.image_key in image_map
            else None,
        )
        for entry in entries
    ]
