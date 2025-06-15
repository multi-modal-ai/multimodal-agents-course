from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    video_path: str | None = None
    image_base64: str | None = None


class ChatResponse(BaseModel):
    response: str
    clip_path: str | None = None


class ProcessVideoRequest(BaseModel):
    video_path: str


class ProcessVideoResponse(BaseModel):
    message: str
    task_id: str


class ResetMemoryResponse(BaseModel):
    message: str
