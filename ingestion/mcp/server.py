import os

from fastmcp import FastMCP
from tools import add_video, get_clips, list_tables

mcp = FastMCP("VideoProcessor")

mcp.add_tool(
    name="add_video",
    description="Add a new video to the database.",
    fn=add_video,
    tags={"video": "ingest"},
)

mcp.add_tool(
    name="list_tables",
    description="List all processed videos in the database.",
    fn=list_tables,
    tags={"video": "list"},
)

mcp.add_tool(
    name="get_clips",
    description="Get a video clip based on a user query.",
    fn=get_clips,
    tags={"video": "search"},
)

if __name__ == "__main__":
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    mcp.run(transport="sse", port=PORT, host=HOST)
    print(f"Server running at http://{HOST}:{PORT}")
