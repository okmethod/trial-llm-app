from typing import Literal

from fastapi import UploadFile
from pydantic import BaseModel


class MessageEntry(BaseModel):
    role: Literal["human", "ai"]
    text: str


class MessageEntryWithImageKey(MessageEntry):
    image_key: str | None = None


class MessageEntryWithImageUri(MessageEntry):
    image_uri: str | None = None


class MessageHistory(BaseModel):
    entries: list[MessageEntryWithImageKey]
    images: list[UploadFile]
