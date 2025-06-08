import logging
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, UploadFile, status
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from src.models.gemini_model import GeminiModelSingleton
from src.schemas.message import MessageEntryWithImageUri, MessageHistory
from src.utils.image_utils import attach_image_uris_to_entries, image_file_to_data_uri

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


def uploadfile_to_image_dict(image: UploadFile, image_dict_factory: Callable[[str], dict[str, Any]]) -> dict[str, Any]:
    return image_dict_factory(image_file_to_data_uri(image))


def output_messeges_summary(messages: list[BaseMessage]) -> None:
    def summarize_message(msg: BaseMessage) -> dict[str, Any]:
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

    logger.info("messages (summary): %s", [summarize_message(m) for m in messages])


def handle_llm_invoke(
    llm_model: str,
    system_prompt: str,
    user_prompt: str,
    image: UploadFile | None = None,
    history: MessageHistory | None = None,
) -> str | list[str | dict[str, object]]:
    messages: list[BaseMessage] = []
    messages.append(SystemMessage(content=system_prompt))

    llm_singleton = GeminiModelSingleton()
    llm_singleton.initialize(llm_model)
    llm = llm_singleton.llm
    image_dict_factory = llm_singleton.image_dict_factory

    if history:
        entries = attach_image_uris_to_entries(history.entries, history.images)
        messages.extend(convert_entries_to_messages(entries, image_dict_factory))

    if image is not None:
        image_dict = uploadfile_to_image_dict(image, image_dict_factory)
        messages.append(HumanMessage(content=[user_prompt, image_dict]))
    else:
        messages.append(HumanMessage(content=[user_prompt]))

    output_messeges_summary(messages)

    try:
        result = llm.invoke(messages)
    except Exception as e:
        logger.exception("Failed to generate text.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    else:
        return result.content
