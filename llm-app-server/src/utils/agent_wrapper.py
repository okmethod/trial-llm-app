import logging
from typing import Any

from fastapi import HTTPException, status

from src.llm_clients.base_client import BaseLLMClient
from src.schemas.message import MessageHistory

logger = logging.getLogger(__name__)


def handle_agent_invoke(
    llm_client: "BaseLLMClient",
    user_prompt: str,
    history: MessageHistory | None = None,
) -> str | dict[str, Any]:
    memory = getattr(llm_client.agent, "memory", None)
    # ConversationBufferMemory型、かつ chat_memory属性を持つ場合、履歴を渡す
    if memory and hasattr(memory, "chat_memory"):
        memory.chat_memory.clear()
        if history:
            for entry in history.entries:
                if hasattr(entry, "role") and entry.text:
                    if entry.role == "human":
                        memory.chat_memory.add_user_message(entry.text)
                    elif entry.role == "ai":
                        memory.chat_memory.add_ai_message(entry.text)
    # Agent は画像非対応とのことなので、画像は memory に追加しない

    try:
        result = llm_client.agent.invoke({"input": user_prompt})
    except Exception as e:
        logger.exception("Failed to generate text via agent.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    else:
        return result["output"] if isinstance(result, dict) and "output" in result else result
