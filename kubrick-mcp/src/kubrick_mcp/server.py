from fastmcp import FastMCP

from kubrick_mcp.prompts import (
    general_system_prompt,
    routing_system_prompt,
    tool_use_system_prompt,
)
from kubrick_mcp.resources import list_tables
from kubrick_mcp.tools import (
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
        fn=routing_system_prompt,
        name="routing_system_prompt",
        description="Latest version of the routing prompt from Opik.",
        tags={"prompt", "routing"},
    )

    mcp.add_prompt(
        fn=tool_use_system_prompt,
        name="tool_use_system_prompt",
        description="Latest version of the tool use prompt from Opik.",
        tags={"prompt", "tool_use"},
    )

    mcp.add_prompt(
        fn=general_system_prompt,
        name="general_system_prompt",
        description="Latest version of the general prompt from Opik.",
        tags={"prompt", "general"},
    )


mcp = FastMCP("VideoProcessor")

add_mcp_prompts(mcp)
add_mcp_tools(mcp)
add_mcp_resources(mcp)
