import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from src.schemas.response_body import SimpleMessageResponse
from src.settings import get_settings
from src.utils.llm_wrapper import handle_llm_invoke

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/gen-text")
async def generate_text(
    prompt: Annotated[str, Form(...)], image: Annotated[UploadFile | None, File()] = None
) -> SimpleMessageResponse:
    settings = get_settings()
    content = handle_llm_invoke(settings.llm_model, prompt, image)
    return SimpleMessageResponse(message=str(content))
