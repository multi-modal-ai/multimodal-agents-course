from contextlib import asynccontextmanager
from enum import Enum
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastmcp.client import Client
from loguru import logger

from agent_api.agent import GroqAgent
from agent_api.config import get_settings
from agent_api.models import (
    ProcessVideoRequest,
    ProcessVideoResponse,
    ResetMemoryResponse,
    UserMessageRequest,
    AssistantMessageResponse,
)

settings = get_settings()

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_FOUND = "not_found"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent = GroqAgent(
        name="kubrick",
        mcp_server=settings.MCP_SERVER,
        disable_tools=["process_video"],
    )
    app.state.bg_task_states = dict()
    yield
    app.state.agent.reset_memory()


app = FastAPI(
    title="Kubrick API",
    description="An AI-powered sports assistant API using OpenAI",
    docs_url="/docs",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """
    Root endpoint that redirects to API documentation
    """
    return {"message": "Welcome to Kubrick API. Visit /docs for documentation"}


@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str, fastapi_request: Request):
    status = fastapi_request.app.state.bg_task_states.get(task_id, TaskStatus.NOT_FOUND)
    return {"task_id": task_id, "status": status}


@app.post("/process-video")
async def process_video(request: ProcessVideoRequest, bg_tasks: BackgroundTasks, fastapi_request: Request):
    """
    Process a video and return the results
    """
    task_id = str(uuid4())
    bg_task_states = fastapi_request.app.state.bg_task_states

    async def background_process_video(video_path: str, task_id: str):
        """
        Background task to process the video
        """
        bg_task_states[task_id] = TaskStatus.IN_PROGRESS

        if not Path(video_path).exists():
            bg_task_states[task_id] = TaskStatus.FAILED
            raise HTTPException(status_code=404, detail="Video file not found")

        try:
            mcp_client = Client(settings.MCP_SERVER)
            async with mcp_client:
                _ = await mcp_client.call_tool(
                    "process_video", {"video_path": request.video_path}
                )
        except Exception as e:
            logger.error(f"Error processing video {video_path}: {e}")
            bg_task_states[task_id] = TaskStatus.FAILED
            raise HTTPException(status_code=500, detail=str(e))
        bg_task_states[task_id] = TaskStatus.COMPLETED

    bg_tasks.add_task(background_process_video, request.video_path, task_id)
    return ProcessVideoResponse(message="Task enqueued for processing", task_id=task_id)


@app.post("/chat", response_model=AssistantMessageResponse)
async def chat(request: UserMessageRequest, fastapi_request: Request):
    """
    Chat with the AI assistant

    Args:
        request: ChatRequest containing the message and optional image URL

    Returns:
        ChatResponse containing the assistant's response
    """
    agent = fastapi_request.app.state.agent
    await agent.setup()

    try:
        response = await agent.chat(request.message, request.video_path, request.image_base64)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset-memory")
async def reset_memory(fastapi_request: Request):
    """
    Reset the memory of the agent
    """
    agent = fastapi_request.app.state.agent
    agent.reset_memory()
    return ResetMemoryResponse(message="Memory reset successfully")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8080)
