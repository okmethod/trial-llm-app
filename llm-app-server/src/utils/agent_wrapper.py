import logging
import uuid
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, status
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from src.llm_clients.base_client import BaseLLMClient
from src.schemas.image import ImageBytes
from src.schemas.message import MessageHistory
from src.utils.image_utils import attach_image_uris_to_entries, bytes_to_image_dict
from src.utils.message_utils import (
    convert_entries_to_messages,
    output_messeges_summary,
)

logger = logging.getLogger(__name__)


def _build_llm_messages(
    user_prompt: str,
    image: ImageBytes | None,
    history: MessageHistory | None,
    image_dict_factory: Callable[[str], dict[str, Any]],
) -> list[BaseMessage]:
    messages: list[BaseMessage] = []
    if history:
        entries = attach_image_uris_to_entries(history.entries, history.images)
        messages.extend(convert_entries_to_messages(entries, image_dict_factory))
    if image is not None:
        image_dict = bytes_to_image_dict(image.data, image.content_type, image_dict_factory)
        messages.append(HumanMessage(content=[user_prompt, image_dict]))
    else:
        messages.append(HumanMessage(content=[user_prompt]))
    return messages


def handle_agent_invoke(
    llm_client: "BaseLLMClient",
    user_prompt: str,
    image: ImageBytes | None = None,
    history: MessageHistory | None = None,
) -> str:
    messages = _build_llm_messages(
        user_prompt,
        image,
        history,
        llm_client.image_dict_factory,
    )
    output_messeges_summary(messages)

    state = {"messages": messages}
    thread_id = str(uuid.uuid4())
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    try:
        result_state = llm_client.agent.invoke(state, config=config)
    except Exception as e:
        logger.exception("Failed to generate text via agent.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    # assistant応答を抽出
    messages = result_state.get("messages", [])
    for msg in reversed(messages):
        if hasattr(msg, "content"):
            content = getattr(msg, "content", "")
            if isinstance(content, str):
                return content
        if isinstance(msg, dict) and msg.get("role") == "assistant":
            content = msg.get("content", "")
            if isinstance(content, str):
                return content
    return str(result_state)
