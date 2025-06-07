import asyncio
import base64
import logging
from typing import Any, TypedDict, cast

from fastapi import HTTPException, UploadFile, status
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.schemas.message import MessageEntryWithImageKey, MessageEntryWithImageUri, MessageHistory

logger = logging.getLogger(__name__)


def image_file_to_data_uri(image: UploadFile) -> str:
    image_bytes = image.file.read() if hasattr(image, "file") else asyncio.run(image.read())
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{image.content_type};base64,{image_b64}"


def convert_entries_with_key_to_uri(
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


def entry_to_message(entry: MessageEntryWithImageUri) -> HumanMessage | AIMessage:
    role = entry.role
    text = entry.text
    image_uri = entry.image_uri
    if role == "ai":
        return AIMessage(content=text)
    if image_uri:
        return HumanMessage(content=[text, {"type": "image_url", "image_url": image_uri}])
    return HumanMessage(content=[text])


def convert_entries_to_messages(entries: list[MessageEntryWithImageUri]) -> list[HumanMessage | AIMessage]:
    return [entry_to_message(entry) for entry in entries]


class GeminiImageDict(TypedDict):
    type: str
    image_url: str


def uploadfile_to_gemini_image_dict(image: UploadFile) -> GeminiImageDict:
    return {
        "type": "image_url",
        "image_url": image_file_to_data_uri(image),
    }


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
    try:
        llm = ChatGoogleGenerativeAI(model=llm_model)
        messages: list[BaseMessage] = []
        messages.append(SystemMessage(content=system_prompt))

        if history:
            entries = convert_entries_with_key_to_uri(history.entries, history.images)
            messages.extend(convert_entries_to_messages(entries))

        if image is not None:
            image_dict = uploadfile_to_gemini_image_dict(image)
            messages.append(HumanMessage(content=[user_prompt, cast(dict[str, Any], image_dict)]))
        else:
            messages.append(HumanMessage(content=[user_prompt]))

        output_messeges_summary(messages)

        result = llm.invoke(messages)
    except Exception as e:
        logger.exception("Failed to generate text.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    else:
        return result.content
