import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from pydantic import AnyUrl, TypeAdapter

POKE_MCP_SERVER_URL = "http://poke-mcp-server:8000"


def call_add_via_mcp(a: int, b: int) -> int:
    async def _call() -> int:
        async with (
            streamablehttp_client(POKE_MCP_SERVER_URL) as (read_stream, write_stream, _),
            ClientSession(read_stream, write_stream) as session,
        ):
            await session.initialize()
            result = await session.call_tool("add", {"a": a, "b": b})
            for content in getattr(result, "content", []):
                if hasattr(content, "text"):
                    return int(content.text)
            msg = "No valid int result from add tool"
            raise ValueError(msg)

    return asyncio.run(_call())


def call_greeting_via_mcp(name: str) -> str:
    async def _call() -> str:
        async with (
            streamablehttp_client(POKE_MCP_SERVER_URL) as (read_stream, write_stream, _),
            ClientSession(read_stream, write_stream) as session,
        ):
            await session.initialize()
            url = TypeAdapter(AnyUrl).validate_python(f"greeting://{name}")
            result = await session.read_resource(url)
            for content in getattr(result, "contents", []):
                if hasattr(content, "text"):
                    return str(content.text)
            msg = "No valid greeting result"
            raise ValueError(msg)

    return asyncio.run(_call())
