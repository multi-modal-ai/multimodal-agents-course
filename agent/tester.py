import asyncio

import pixeltable as pxt
from fastmcp import Client


async def test_mcp():
    mcp_server = Client("http://127.0.0.1:8000/sse")
    async with mcp_server:
        tools = await mcp_server.list_tools()
        pxt.func.tools.Tool()
        print(f"Discovered tools: {tools}")


if __name__ == "__main__":
    asyncio.run(test_mcp())
