from collections.abc import Callable
from typing import Any

from langchain.agents import AgentExecutor, AgentType, initialize_agent
from langchain_core.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI

from src.llm_clients.base_client import BaseLLMClient, ModelNotInitializedError


class GeminiClientSingleton(BaseLLMClient):
    _instance: "GeminiClientSingleton | None" = None
    _llm_instance: ChatGoogleGenerativeAI | None = None
    _agent_instance: AgentExecutor | None = None
    _image_dict_factory: Callable[[str], dict[str, Any]] | None = None

    def __new__(cls) -> "GeminiClientSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, llm_model: str) -> None:
        self._llm_instance = ChatGoogleGenerativeAI(model=llm_model)
        self._image_dict_factory = self.cast_to_gemini_image_dict
        tools: list[Tool] = []  # TODO: Toolを追加する
        self._agent_instance = initialize_agent(
            tools,
            self._llm_instance,
            agent=AgentType.OPENAI_FUNCTIONS,  # Function Calling を利用
            verbose=True,
        )

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
    def agent(self) -> AgentExecutor:
        if self._agent_instance is None:
            raise ModelNotInitializedError
        return self._agent_instance

    @property
    def image_dict_factory(self) -> Callable[[str], dict[str, Any]]:
        if self._image_dict_factory is None:
            raise ModelNotInitializedError
        return self._image_dict_factory
