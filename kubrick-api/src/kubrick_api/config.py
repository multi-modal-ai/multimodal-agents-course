from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="agent-api/.env", extra="ignore", env_file_encoding="utf-8")

    # --- Provider selection ---
    LLM_PROVIDER: Literal["groq", "minimax"] = "groq"

    # --- GROQ Configuration ---
    GROQ_API_KEY: str | None = None
    GROQ_ROUTING_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    GROQ_TOOL_USE_MODEL: str = "meta-llama/llama-4-maverick-17b-128e-instruct"
    GROQ_IMAGE_MODEL: str = "meta-llama/llama-4-maverick-17b-128e-instruct"
    GROQ_GENERAL_MODEL: str = "meta-llama/llama-4-maverick-17b-128e-instruct"

    # --- MiniMax Configuration ---
    MINIMAX_API_KEY: str | None = None
    MINIMAX_REGION: Literal["global_en", "cn_zh"] = "global_en"
    MINIMAX_BASE_URL: str | None = None
    MINIMAX_MODEL: str = "MiniMax-M3.1-Flash"
    MINIMAX_ROUTING_MODEL: str | None = None
    MINIMAX_TOOL_USE_MODEL: str | None = None
    MINIMAX_GENERAL_MODEL: str | None = None
    MINIMAX_REASONING_EFFORT: Literal["low", "medium", "high", "xhigh", "max"] = "max"

    # --- Comet ML & Opik Configuration ---
    OPIK_API_KEY: str | None = Field(default=None, description="API key for Comet ML and Opik services.")
    OPIK_WORKSPACE: str = "default"
    OPIK_PROJECT: str = Field(
        default="kubrick-api",
        description="Project name for Comet ML and Opik tracking.",
    )

    # --- Memory Configuration ---
    AGENT_MEMORY_SIZE: int = 20

    # --- MCP Configuration ---
    MCP_SERVER: str = "http://kubrick-mcp:9090/mcp"

    # --- Disable Nest Asyncio ---
    DISABLE_NEST_ASYNCIO: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get the application settings.

    Returns:
        Settings: The application settings.
    """
    return Settings()
