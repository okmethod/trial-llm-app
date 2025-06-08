import json
import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile
from pydantic import TypeAdapter, ValidationError

from src.models.gemini_model import GeminiModelSingleton
from src.schemas.message import MessageEntryWithImageKey, MessageHistory
from src.schemas.response_body import SimpleMessageResponse
from src.settings import get_settings
from src.utils.llm_wrapper import handle_llm_invoke

router = APIRouter()
logger = logging.getLogger(__name__)

llm_singleton = GeminiModelSingleton()


def _parse_history_entries(history_json: str) -> list[MessageEntryWithImageKey]:
    try:
        entries_type = MessageHistory.model_fields["entries"].annotation
        return TypeAdapter(entries_type).validate_python(json.loads(history_json))
    except ValidationError as e:
        logger.warning("Failed to history_json: %s", e)
        return []


@router.post("/gen-text")
async def generate_text(
    prompt: Annotated[str, Form(...)],
    image: Annotated[UploadFile | None, File()] = None,
    history_json: Annotated[str | None, Form()] = None,
    history_images: Annotated[list[UploadFile] | None, File()] = None,
) -> SimpleMessageResponse:
    settings = get_settings()

    history = (
        MessageHistory(
            entries=_parse_history_entries(history_json) if history_json else [],
            images=history_images or [],
        )
        if history_json
        else None
    )

    llm_singleton.initialize(settings.llm_model)

    content = handle_llm_invoke(
        system_prompt=settings.system_prompt,
        user_prompt=prompt,
        image=image,
        history=history,
        llm_singleton=llm_singleton,
    )
    return SimpleMessageResponse(message=str(content))
