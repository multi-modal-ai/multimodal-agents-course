from pydantic import BaseModel, Field


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
    

class RoutingResponseModel(BaseModel):
    tool_use: bool = Field(description="Whether the user's question requires a tool call.")

    
class GeneralResponseModel(BaseModel):
    content: str = Field(description="Your response to the user's question.")

    
class VideoClipResponseModel(BaseModel):
    clip_path: str = Field(description="The path to the generated clip.")
    content: str = Field(description="A message prompting the user to view the video clip.")

