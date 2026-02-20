from fastmcp import FastMCP

mcp = FastMCP("Test Server")

@mcp.tool
def ping() -> str:
    """A command to test that the MCP server is connected"""
    return "pong"

if __name__ == "__main__": 
    mcp.run()