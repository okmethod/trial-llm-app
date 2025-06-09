import json
import logging
from collections.abc import Generator
from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import TypeAdapter, ValidationError

from src.llm_clients.gemini_client import GeminiClientSingleton
from src.schemas.image import ImageBytes
from src.schemas.message import MessageEntryWithImageKey, MessageHistory
from src.schemas.response_body import SimpleMessageResponse
from src.settings import get_settings
from src.utils.image_utils import uploadfile_to_image_bytes
from src.utils.llm_wrapper import handle_llm_invoke, handle_llm_stream
from src.utils.message_utils import build_message_history

router = APIRouter()
logger = logging.getLogger(__name__)

llm_client = GeminiClientSingleton()


def _parse_history_entries(history_json: str) -> list[MessageEntryWithImageKey]:
    try:
        entries_type = MessageHistory.model_fields["entries"].annotation
        return TypeAdapter(entries_type).validate_python(json.loads(history_json))
    except ValidationError as e:
        logger.warning("Failed to history_json: %s", e)
        return []


@dataclass
class LLMContext:
    system_prompt: str
    image: ImageBytes | None
    history: MessageHistory | None


async def _prepare_llm_context(
    image: UploadFile | None,
    history_json: str | None,
    history_images: list[UploadFile] | None,
) -> LLMContext:
    settings = get_settings()
    image_byte_obj = await uploadfile_to_image_bytes(image) if image else None
    entries = _parse_history_entries(history_json) if history_json else []
    images = [await uploadfile_to_image_bytes(img) for img in history_images] if history_images else []
    history = build_message_history(entries, images) if entries or images else None
    llm_client.initialize(settings.llm_model, settings.system_prompt)
    return LLMContext(system_prompt=settings.system_prompt, image=image_byte_obj, history=history)


@router.post("/gen-text")
async def generate_text(
    prompt: Annotated[str, Form(...)],
    image: Annotated[UploadFile | None, File()] = None,
    history_json: Annotated[str | None, Form()] = None,
    history_images: Annotated[list[UploadFile] | None, File()] = None,
) -> SimpleMessageResponse:
    ctx = await _prepare_llm_context(image, history_json, history_images)

    content = handle_llm_invoke(
        llm_client=llm_client,
        system_prompt=ctx.system_prompt,
        user_prompt=prompt,
        image=ctx.image,
        history=ctx.history,
    )

    return SimpleMessageResponse(message=str(content))


@router.post("/gen-text-stream")
async def generate_text_stream(
    prompt: Annotated[str, Form(...)],
    image: Annotated[UploadFile | None, File()] = None,
    history_json: Annotated[str | None, Form()] = None,
    history_images: Annotated[list[UploadFile] | None, File()] = None,
) -> StreamingResponse:
    ctx = await _prepare_llm_context(image, history_json, history_images)

    def _stream_generator() -> Generator[str, None, None]:
        yield from handle_llm_stream(
            llm_client=llm_client,
            system_prompt=ctx.system_prompt,
            user_prompt=prompt,
            image=ctx.image,
            history=ctx.history,
        )

    return StreamingResponse(_stream_generator(), media_type="text/plain")
