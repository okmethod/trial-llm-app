from mcp.server.fastmcp import FastMCP


def register_greeting_tools(mcp: FastMCP) -> None:
    @mcp.resource("greeting://{name}")
    def get_greeting(name: str) -> str:
        """Get a personalized greeting"""
        return f"Hello, {name}!"
