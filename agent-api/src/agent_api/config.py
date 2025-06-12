from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )

    # --- GROQ Configuration ---
    GROQ_API_KEY: str
    GROQ_ROUTING_MODEL: str = "llama3-70b-8192"
    GROQ_TOOL_USE_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_GENERAL_MODEL: str = "llama3-70b-8192"

    # --- Comet ML & Opik Configuration ---
    OPIK_API_KEY: str
    OPIK_WORKSPACE: str = "default"
    OPIK_PROJECT: str = "kubrick-api"

    # --- Memory Configuration ---
    AGENT_MEMORY_SIZE: int = 20

    # --- MCP Configuration ---
    MCP_SERVER: str = "http://mcp-server:9090/mcp"


settings = Settings()
