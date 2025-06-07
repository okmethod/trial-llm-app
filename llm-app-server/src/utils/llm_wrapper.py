import logging
from typing import Any

from fastapi import HTTPException, status
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)


def handle_llm_invoke(llm_model: str, prompt: str) -> str | list[str | dict[Any, Any]]:
    try:
        llm = ChatGoogleGenerativeAI(model=llm_model)
        result = llm.invoke(prompt)
    except Exception as e:
        logger.exception("Failed to generate text.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    else:
        return result.content
