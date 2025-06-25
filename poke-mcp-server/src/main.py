# https://github.com/modelcontextprotocol/python-sdk/tree/main?tab=readme-ov-file#quickstart

from mcp.server.fastmcp import FastMCP

from src.greeting_tools import register_greeting_tools
from src.math_tools import register_math_tools

mcp = FastMCP("StatelessServer", stateless_http=True)

register_math_tools(mcp)
register_greeting_tools(mcp)

mcp.run(transport="streamable-http")
