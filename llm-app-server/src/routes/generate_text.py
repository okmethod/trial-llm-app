import logging

from fastapi import APIRouter, HTTPException, status
from langchain_google_genai import ChatGoogleGenerativeAI

from src.schemas.generate_text import LLMRequest, LLMResponse
from src.settings import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/gen-text")
async def generate_text(request: LLMRequest) -> LLMResponse:
    settings = get_settings()
    try:
        llm = ChatGoogleGenerativeAI(model=settings.llm_model)
        result = llm.invoke(request.prompt)
        return LLMResponse(result=result.content)
    except Exception as e:
        logger.exception("Failed to generate text.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
