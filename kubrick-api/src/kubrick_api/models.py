from pydantic import BaseModel, Field


class ProcessVideoRequest(BaseModel):
    video_path: str


class ProcessVideoResponse(BaseModel):
    message: str
    task_id: str


class UserMessageRequest(BaseModel):
    message: str
    video_path: str | None = None
    image_base64: str | None = None


class AssistantMessageResponse(BaseModel):
    message: str
    clip_path: str | None = None


class ResetMemoryResponse(BaseModel):
    message: str


class VideoUploadResponse(BaseModel):
    message: str
    video_path: str | None = None
    task_id: str | None = None


# -- LLM Structured Outputs Models --


class RoutingResponseModel(BaseModel):
    tool_use: bool = Field(
        description="Whether the user's question requires a tool call."
    )


class GeneralResponseModel(BaseModel):
    message: str = Field(
        description="Your response to the user's question, that needs to follow Kubrick's style and personality"
    )


class VideoClipResponseModel(BaseModel):
    message: str = Field(
        description="A fun and engaging message to the user, asking them to watch the video clip, that needs to follow Kubrick's style and personality"
    )
    clip_path: str = Field(description="The path to the generated clip.")
