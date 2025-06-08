import logging

from fastapi import HTTPException, UploadFile, status
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from src.models.base_model import BaseModelSingleton
from src.schemas.message import MessageHistory
from src.utils.image_utils import attach_image_uris_to_entries
from src.utils.message_utils import (
    convert_entries_to_messages,
    output_messeges_summary,
    uploadfile_to_image_dict,
)

logger = logging.getLogger(__name__)


def handle_llm_invoke(
    llm_singleton: "BaseModelSingleton",
    system_prompt: str,
    user_prompt: str,
    image: UploadFile | None = None,
    history: MessageHistory | None = None,
) -> str | list[str | dict[str, object]]:
    messages: list[BaseMessage] = []
    messages.append(SystemMessage(content=system_prompt))

    if history:
        entries = attach_image_uris_to_entries(history.entries, history.images)
        messages.extend(convert_entries_to_messages(entries, llm_singleton.image_dict_factory))

    if image is not None:
        image_dict = uploadfile_to_image_dict(image, llm_singleton.image_dict_factory)
        messages.append(HumanMessage(content=[user_prompt, image_dict]))
    else:
        messages.append(HumanMessage(content=[user_prompt]))

    output_messeges_summary(messages)

    try:
        result = llm_singleton.llm.invoke(messages)
    except Exception as e:
        logger.exception("Failed to generate text.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    else:
        if not isinstance(result, BaseMessage):
            logger.warning("llm.invoke did not return BaseMessage, got: %s", type(result))
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return result.content
