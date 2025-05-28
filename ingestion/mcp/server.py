import os

from fastmcp import FastMCP
from tools import get_clip_by_caption_sim, get_clip_by_image_sim, get_clip_by_speech_sim, list_tables

mcp = FastMCP("VideoProcessor")

mcp.add_tool(
    name="list_tables",
    description="List all processed videos in the database.",
    fn=list_tables,
    tags={"video": "list"},
)

mcp.add_tool(
    name="get_clip_by_speech_sim",
    description="Get a video clip based on a user query using the transcripts index.",
    fn=get_clip_by_speech_sim,
    tags={"video", "search", "transcript"},
)

mcp.add_tool(
    name="get_clip_by_image_sim",
    description="Get a video clip based on a user query using the image index.",
    fn=get_clip_by_image_sim,
    tags={"video", "search", "image"},
)

mcp.add_tool(
    name="get_clip_by_caption_sim",
    description="Get a video clip based on a user query using the caption index.",
    fn=get_clip_by_caption_sim,
    tags={"video", "search", "caption"},
)

if __name__ == "__main__":
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    mcp.run(transport="sse", port=PORT, host=HOST)
    print(f"Server running at http://{HOST}:{PORT}")
