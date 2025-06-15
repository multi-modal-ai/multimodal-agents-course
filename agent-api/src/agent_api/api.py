import tempfile
from contextlib import asynccontextmanager
from enum import Enum
from pathlib import Path
from shutil import copyfileobj
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, Request, UploadFile
from fastmcp.client import Client
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from agent_api.agent import GroqAgent
from agent_api.config import settings
from agent_api.models import ChatRequest, ChatResponse, ResetMemoryResponse


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_FOUND = "not_found"


# FIXME: move this enum outside app definition / bound size with deque or clean it

bg_task_states = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.agent = GroqAgent(
        name="kubrick",
        mcp_server=settings.MCP_SERVER,
        active_tools=["process_video", "get_video_clip_from_image"],
    )
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


async def background_process_video(video_path: str, task_id: str):
    bg_task_states[task_id] = TaskStatus.IN_PROGRESS

    if not Path(video_path).exists():
        bg_task_states[task_id] = TaskStatus.FAILED
        logger.error(f"Video file not found at {video_path}")
        return

    try:
        mcp_client = Client(settings.MCP_SERVER)
        async with mcp_client:
            processed_video_url = await mcp_client.call_tool("process_video", {"video_path": video_path})

        processed_videos[task_id] = {
            "videoUrl": processed_video_url,
            "title": Path(video_path).name,
        }

    except Exception as e:
        logger.error(f"Error processing video {video_path}: {e}")
        bg_task_states[task_id] = TaskStatus.FAILED
        return

    bg_task_states[task_id] = TaskStatus.COMPLETED


processed_videos = {}


@app.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    status = bg_task_states.get(task_id, TaskStatus.NOT_FOUND)

    response = {"task_id": task_id, "status": status}

    if status == TaskStatus.COMPLETED:
        video_info = processed_videos.get(task_id)
        if video_info:
            response.update(video_info)
        else:
            response.update({"videoUrl": "", "title": ""})

    return response


@app.post("/process-video")
async def process_video(file: UploadFile = File(...), bg_tasks: BackgroundTasks = None):
    """
    Accept uploaded video file and enqueue background processing task.
    """
    task_id = str(uuid4())

    # Save uploaded file to a temporary path
    temp_dir = Path(tempfile.gettempdir())
    video_path = temp_dir / f"{task_id}_{file.filename}"

    with open(video_path, "wb") as buffer:
        copyfileobj(file.file, buffer)

    bg_tasks.add_task(background_process_video, str(video_path), task_id)

    return {"message": "Task enqueued for processing", "taskId": task_id}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, fastapi_request: Request):
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
        response = await agent.chat(request.message, request.video_path)
        return ChatResponse(response=response)
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

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8080)
