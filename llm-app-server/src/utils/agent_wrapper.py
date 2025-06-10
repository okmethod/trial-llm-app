import logging
import uuid

from fastapi import HTTPException, status
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from src.llm_clients.base_client import BaseLLMClient
from src.schemas.image import ImageBytes
from src.schemas.message import MessageHistory
from src.utils.message_utils import build_langchain_messages, output_messeges_summary

logger = logging.getLogger(__name__)


def handle_agent_invoke(
    llm_client: "BaseLLMClient",
    user_prompt: str,
    image: ImageBytes | None = None,
    history: MessageHistory | None = None,
) -> str:
    messages = build_langchain_messages(
        None,  # system_prompt は 設定済み
        user_prompt,
        image,
        history,
        llm_client.image_dict_factory,
    )
    output_messeges_summary(messages)

    state = {"messages": messages}
    thread_id = str(uuid.uuid4())
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    try:
        result_state = llm_client.agent.invoke(state, config=config)
    except Exception as e:
        logger.exception("Failed to generate text via agent.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e

    messages = result_state.get("messages", [])
    for msg in reversed(messages):  # 最新のメッセージを取得
        if isinstance(msg, AIMessage) and isinstance(msg.content, str):
            return msg.content
    return str(result_state)
