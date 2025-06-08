from collections.abc import Callable
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI

from src.models.base_model import BaseModelSingleton, ModelNotInitializedError


class GeminiModelSingleton(BaseModelSingleton):
    _instance: "GeminiModelSingleton | None" = None
    _llm_instance: ChatGoogleGenerativeAI | None = None
    _image_dict_factory: Callable[[str], dict[str, Any]] | None = None

    def __new__(cls) -> "GeminiModelSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, llm_model: str) -> None:
        self._llm_instance = ChatGoogleGenerativeAI(model=llm_model)
        self._image_dict_factory = self.cast_to_gemini_image_dict

    @staticmethod
    def cast_to_gemini_image_dict(image_uri: str) -> dict[str, Any]:
        """Geminiに合わせた形式の画像辞書を生成する"""
        return {"type": "image_url", "image_url": image_uri}

    @property
    def llm(self) -> ChatGoogleGenerativeAI:
        if self._llm_instance is None:
            raise ModelNotInitializedError
        return self._llm_instance

    @property
    def image_dict_factory(self) -> Callable[[str], dict[str, Any]]:
        if self._image_dict_factory is None:
            raise ModelNotInitializedError
        return self._image_dict_factory
