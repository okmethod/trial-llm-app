from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from langchain.agents import AgentExecutor
from langchain_core.language_models.base import BaseLanguageModel


class ModelNotInitializedError(Exception):
    """モデルが初期化されていない場合に発生するエラー"""


class BaseLLMClient(ABC):
    @abstractmethod
    def initialize(self, llm_model: str) -> None:
        """LLMインスタンス等を初期化する"""

    @property
    @abstractmethod
    def llm(self) -> BaseLanguageModel[Any]:
        """BaseLanguageModel のサブクラスである LLMインスタンス"""

    @property
    @abstractmethod
    def agent(self) -> AgentExecutor:
        """Function Calling 対応の AgentExecutorインスタンス"""

    @property
    @abstractmethod
    def image_dict_factory(self) -> Callable[[str], dict[str, Any]]:
        """各プロバイダに合わせた形の画像辞書を生成する関数"""
