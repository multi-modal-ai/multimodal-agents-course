from pydantic import BaseModel, Field

class RoutingResponseModel(BaseModel):
    tool_use: bool = Field(description="Whether the user's question requires a tool call.")
    
class GeneralResponseModel(BaseModel):
    content: str = Field(description="Your response to the user's question.")
    
class VideoClipResponseModel(BaseModel):
    clip_path: str = Field(description="The path to the generated clip.")
    content: str = Field(description="A message prompting the user to view the video clip.")
