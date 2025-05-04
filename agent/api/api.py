from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agent.agent import Agent
from agent.core.prompts import SPORT_ASSISTANT_SYSTEM_PROMPT

app = FastAPI(
    title="Sport Assistant API",
    description="An AI-powered sports assistant API using OpenAI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


# Initialize the agent
agent = Agent(
    name="sport_assistant",
    system_prompt=SPORT_ASSISTANT_SYSTEM_PROMPT.prompt,
)


@app.get("/")
async def root():
    """
    Root endpoint that redirects to API documentation
    """
    return {"message": "Welcome to Sport Assistant API. Visit /docs for documentation"}


# TODO: Tell Pixeltable to create async version of inserts?
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Chat with the AI assistant

    Args:
        request: ChatRequest containing the message and optional image URL

    Returns:
        ChatResponse containing the assistant's response
    """
    try:
        # Get response from agent
        response = agent.chat(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
