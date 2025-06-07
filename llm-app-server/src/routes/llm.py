import logging

from fastapi import APIRouter, HTTPException, status
from langchain_google_genai import ChatGoogleGenerativeAI

from src.schemas.llm import LLMRequest, LLMResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/gen-text")
async def llm_endpoint(request: LLMRequest) -> LLMResponse:
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")  # APIキーは環境変数で設定
        result = llm.invoke(request.prompt)
        return LLMResponse(result=result.content)
    except Exception as e:
        logger.exception("Failed to generate text.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
