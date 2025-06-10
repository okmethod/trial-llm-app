from collections.abc import Callable
from typing import Any

from langchain.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import create_react_agent

from src.llm_clients.base_client import BaseLLMClient, ModelNotInitializedError
from src.tools.utils import get_current_utc_time


class GeminiClientSingleton(BaseLLMClient):
    _instance: "GeminiClientSingleton | None" = None
    _llm_instance: ChatGoogleGenerativeAI | None = None
    _agent_instance: CompiledGraph | None = None
    _image_dict_factory: Callable[[str], dict[str, Any]] | None = None

    def __new__(cls) -> "GeminiClientSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, llm_model: str, system_prompt: str) -> None:
        self._llm_instance = ChatGoogleGenerativeAI(model=llm_model)
        self._image_dict_factory = self.cast_to_gemini_image_dict
        self._agent_instance = self._create_agent(self._llm_instance, system_prompt)

    def _create_agent(self, llm: ChatGoogleGenerativeAI, system_prompt: str) -> CompiledGraph:
        tools: list[Tool] = [
            Tool(
                name="get_current_utc_time",
                func=get_current_utc_time,
                description="現在日時(UTC)を ISO8601形式で返す。引数は無し。",
            )
        ]
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{messages}"),
            ]
        )
        memory = MemorySaver()
        return create_react_agent(
            model=llm,
            tools=tools,
            prompt=prompt,
            checkpointer=memory,
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
    def agent(self) -> CompiledGraph:
        if self._agent_instance is None:
            raise ModelNotInitializedError
        return self._agent_instance

    @property
    def image_dict_factory(self) -> Callable[[str], dict[str, Any]]:
        if self._image_dict_factory is None:
            raise ModelNotInitializedError
        return self._image_dict_factory
