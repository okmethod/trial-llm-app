import logging
from collections.abc import Callable, Generator
from typing import Any

from fastapi import HTTPException, status
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

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
    system_prompt: str,
    user_prompt: str,
    image: ImageBytes | None,
    history: MessageHistory | None,
    image_dict_factory: Callable[[str], dict[str, Any]],
) -> list[BaseMessage]:
    messages: list[BaseMessage] = [SystemMessage(content=system_prompt)]
    if history:
        entries = attach_image_uris_to_entries(history.entries, history.images)
        messages.extend(convert_entries_to_messages(entries, image_dict_factory))
    if image is not None:
        image_dict = bytes_to_image_dict(image.data, image.content_type, image_dict_factory)
        messages.append(HumanMessage(content=[user_prompt, image_dict]))
    else:
        messages.append(HumanMessage(content=[user_prompt]))
    return messages


def handle_llm_invoke(
    llm_client: "BaseLLMClient",
    system_prompt: str,
    user_prompt: str,
    image: ImageBytes | None = None,
    history: MessageHistory | None = None,
) -> str | list[str | dict[str, object]]:
    messages = _build_llm_messages(
        system_prompt,
        user_prompt,
        image,
        history,
        llm_client.image_dict_factory,
    )
    output_messeges_summary(messages)

    try:
        result = llm_client.llm.invoke(messages)
    except Exception as e:
        logger.exception("Failed to generate text.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    else:
        if not isinstance(result, BaseMessage):
            logger.warning("llm.invoke did not return BaseMessage, got: %s", type(result))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return result.content


def handle_llm_stream(
    llm_client: "BaseLLMClient",
    system_prompt: str,
    user_prompt: str,
    image: ImageBytes | None = None,
    history: MessageHistory | None = None,
) -> Generator[str, None, None]:
    messages = _build_llm_messages(
        system_prompt,
        user_prompt,
        image,
        history,
        llm_client.image_dict_factory,
    )
    output_messeges_summary(messages)

    def _raise_stream_error(chunk_type: type) -> None:
        logger.warning("llm.stream did not return BaseMessage, got: %s", chunk_type)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        for chunk in llm_client.llm.stream(messages):
            if not isinstance(chunk, BaseMessage):
                _raise_stream_error(type(chunk))
            yield chunk.content
    except Exception as e:
        logger.exception("Failed to stream generate text.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
