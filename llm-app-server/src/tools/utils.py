from datetime import UTC, datetime

from langchain_core.tools import tool


@tool
def get_current_utc_time() -> str:
    """現在日時(UTC)を ISO8601形式で返す"""
    return datetime.now(tz=UTC).isoformat()
