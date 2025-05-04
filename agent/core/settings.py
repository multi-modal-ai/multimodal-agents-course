from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")

    OPENAI_API_KEY: str
    COMET_API_KEY: str | None = Field(default=None, description="API key for Comet ML and Opik services.")
    COMET_PROJECT: str = Field(
        default="multimodal_agents_course",
        description="Project name for Comet ML and Opik tracking.",
    )


settings = Settings()
