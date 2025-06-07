import asyncio
import base64
import logging
from typing import Any, TypedDict, cast

from fastapi import HTTPException, UploadFile, status
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)


class GeminiImageDict(TypedDict):
    type: str
    image_url: str


def uploadfile_to_gemini_image_dict(image: UploadFile) -> GeminiImageDict:
    """
    UploadFile を Gemini API用の image_dict形式に変換
    """
    image_bytes = image.file.read() if hasattr(image, "file") else asyncio.run(image.read())
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    return {
        "type": "image_url",
        "image_url": f"data:{image.content_type};base64,{image_b64}",
    }


def handle_llm_invoke(
    llm_model: str, prompt: str, image: UploadFile | None = None
) -> str | list[str | dict[str, object]]:
    try:
        llm = ChatGoogleGenerativeAI(model=llm_model)
        if image is not None:
            image_dict = uploadfile_to_gemini_image_dict(image)
            messages = [HumanMessage(content=[prompt, cast(dict[str, Any], image_dict)])]
            result = llm.invoke(messages)
        else:
            result = llm.invoke(prompt)
    except Exception as e:
        logger.exception("Failed to generate text.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    else:
        return result.content
