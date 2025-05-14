import os

from fastmcp import FastMCP
from tools import add_video

### DISABLE FASTAPI ###
"""
app = FastAPI(
    title="Video Processor",
    description="A FastAPI application for video processing.",
    version="1.0.0",
)
mcp = FastMCP("VideoProcessor")

app.add_api_route(
    "/add_video/{video_name}",
    add_video,
    methods=["POST"],
    description="Add a new video to the database.",
)

app.add_api_route(
    "/list_videos",
    list_tables,
    methods=["GET"],
    description="List all processed videos in the database.",
)

app.add_api_route(
    "/fetch_clip",
    get_clips,
    methods=["POST"],
    description="Fetch a video clip based on a user query.",
)

mcp_server = mcp.from_fastapi(app)

"""

mcp = FastMCP("VideoProcessor")

mcp.add_tool(
    name="add_video",
    description="Add a new video to the database.",
    fn=add_video,
    tags={"video": "ingest"},
)

if __name__ == "__main__":
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    mcp.run(transport="sse", port=PORT, host=HOST)
    print(f"Server running at http://{HOST}:{PORT}")
