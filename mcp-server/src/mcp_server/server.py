from fastmcp import FastMCP

from mcp_server.prompts import struct_output_prompt, system_prompt
from mcp_server.resources import list_tables
from mcp_server.tools import (
    ask_question_about_video,
    get_video_clip_from_image,
    get_video_clip_from_user_query,
    process_video,
)


def add_mcp_tools(mcp: FastMCP):
    mcp.add_tool(
        name="process_video",
        description="Process a video file and prepare it for searching.",
        fn=process_video,
        tags={"video", "process"},
    )

    mcp.add_tool(
        name="get_video_clip_from_user_query",
        description="Use this tool to get a video clip from a video file based on a user query or question.",
        fn=get_video_clip_from_user_query,
        tags={"video", "clip", "query", "question"},
    )

    mcp.add_tool(
        name="get_video_clip_from_image",
        description="Use this tool to get a video clip from a video file based on a user image.",
        fn=get_video_clip_from_image,
        tags={"video", "clip", "image"},
    )

    mcp.add_tool(
        name="ask_question_about_video",
        description="Use this tool to get an answer to a question about the video.",
        fn=ask_question_about_video,
        tags={"ask", "question", "information"},
    )


def add_mcp_resources(mcp: FastMCP):
    mcp.add_resource_fn(
        fn=list_tables,
        uri="file:///app/.records/records.json",
        name="list_tables",
        description="List all video indexes currently available.",
        tags={"resource", "all"},
    )


def add_mcp_prompts(mcp: FastMCP):
    mcp.add_prompt(
        fn=struct_output_prompt,
        name="struct_output_prompt",
        description="Latest version of the response prompt from Opik.",
        tags={"prompt", "structured.output"},
    )

    mcp.add_prompt(
        fn=system_prompt,
        name="system_prompt",
        description="Latest version of the system prompt from Opik.",
        tags={"prompt", "system"},
    )


mcp = FastMCP("VideoProcessor")

add_mcp_prompts(mcp)
add_mcp_tools(mcp)
add_mcp_resources(mcp)

if __name__ == "__main__":
    mcp.run(host="0.0.0.0", port=8000, transport="streamable-http")
