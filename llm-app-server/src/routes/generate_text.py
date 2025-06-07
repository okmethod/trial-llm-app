import logging

from fastapi import APIRouter

from src.schemas.generate_text import LLMRequest, LLMResponse
from src.settings import get_settings
from src.utils.llm_wrapper import handle_llm_invoke

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/gen-text")
async def generate_text(request: LLMRequest) -> LLMResponse:
    settings = get_settings()
    content = handle_llm_invoke(settings.llm_model, request.prompt)
    return LLMResponse(answer=str(content))
