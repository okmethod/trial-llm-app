import logging
from collections.abc import Callable
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from src.schemas.image import ImageBytes
from src.schemas.message import MessageEntryWithImageKey, MessageEntryWithImageUri, MessageHistory

logger = logging.getLogger(__name__)


def entry_to_message(
    entry: MessageEntryWithImageUri,
    image_dict_factory: Callable[[str], dict[str, Any]],
) -> HumanMessage | AIMessage:
    role = entry.role
    text = entry.text
    image_uri = entry.image_uri
    if role == "ai":
        return AIMessage(content=text)
    if image_uri:
        image_dict = image_dict_factory(image_uri)
        return HumanMessage(content=[text, image_dict])
    return HumanMessage(content=[text])


def convert_entries_to_messages(
    entries: list[MessageEntryWithImageUri],
    image_dict_factory: Callable[[str], dict[str, Any]],
) -> list[HumanMessage | AIMessage]:
    return [entry_to_message(entry, image_dict_factory) for entry in entries]


def build_message_history(
    entries: list[MessageEntryWithImageKey], images: list[ImageBytes] | None
) -> MessageHistory | None:
    return MessageHistory(entries=entries, images=images or [])


def output_messeges_summary(messages: list[BaseMessage]) -> None:
    def _summarize_message(msg: BaseMessage) -> dict[str, Any]:
        if isinstance(msg, SystemMessage):
            return {"type": "system", "text": msg.content}
        if isinstance(msg, HumanMessage):
            content = msg.content
            text = content[0] if isinstance(content, list) else content
            has_image = any(isinstance(c, dict) and c.get("type") == "image_url" for c in content[1:])
            return {"type": "human", "text": text, "has_image": has_image}
        if isinstance(msg, AIMessage):
            return {"type": "ai", "text": msg.content}
        return {"type": str(type(msg)), "text": str(msg)}

    logger.info("messages (summary): %s", [_summarize_message(m) for m in messages])
