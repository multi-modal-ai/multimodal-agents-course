import asyncio

from fastmcp import Client


async def test_mcp():
    mcp_client = Client("http://127.0.0.1:8080/sse")
    async with mcp_client:
        tools = await mcp_client.list_tools()
        for tool in tools:
            print(f"Tool name: {tool.name}")
            print(f"Tool description: {tool.description}")
            print()

        response = await mcp_client.call_tool(
            "get_clips",
            {
                "video_name": "2018_portugal_vs_spain_T0h0m_0h5m",
                "user_query": "Cristiano Ronaldo penalty",
                "top_k": 1,
            },
        )
        # print(f"Response from add_video: {response}")

        tables = await mcp_client.call_tool("list_tables")


if __name__ == "__main__":
    asyncio.run(test_mcp())
