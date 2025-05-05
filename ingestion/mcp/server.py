from fastmcp import FastMCP
from tools import add_video, get_clips, list_tables

mcp = FastMCP("VideoProcessor")

mcp.add_tool(
    name="add_video",
    fn=add_video,
    description="Add a new video to database.",
    tags=["video", "ingestion"],
)


mcp.add_tool(
    name="fetch_clip",
    fn=get_clips,
    description="Fetch a video clip based on a user query.",
    tags=["video", "query"],
)

mcp.add_tool(
    name="list_videos",
    fn=list_tables,
    description="List all processed videos in database.",
    tags=["video", "list"],
)

if __name__ == "__main__":
    # FIXME: this is dirty, pass the config
    # or, use uv run fastmcp run ... and cli pass the args
    cfg = {"host": "127.0.0.1", "port": 8000, "transport": "sse"}
    mcp.run(**cfg)
