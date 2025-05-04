from pydantic import BaseModel


# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
