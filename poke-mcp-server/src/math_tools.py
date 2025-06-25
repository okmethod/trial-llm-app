from mcp.server.fastmcp import FastMCP


def register_math_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    def add(a: int, b: int) -> int:
        """Add two numbers"""
        return a + b
