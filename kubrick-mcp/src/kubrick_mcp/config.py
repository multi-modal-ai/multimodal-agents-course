from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="mcp-server/.env", extra="ignore", env_file_encoding="utf-8"
    )

    # --- OPIK Configuration ---
    OPIK_API_KEY: str
    OPIK_WORKSPACE: str = "default"
    OPIK_PROJECT: str = "mcp-server"

    # --- OPENAI Configuration ---
    OPENAI_API_KEY: str
    AUDIO_TRANSCRIPT_MODEL: str = "gpt-4o-mini-transcribe"
    IMAGE_CAPTION_MODEL: str = "gpt-4o-mini"

    # --- Video Ingestion Configuration ---
    SPLIT_FPS: float = 1.0
    AUDIO_CHUNK_LENGTH: int = 10
    AUDIO_OVERLAP_SECONDS: int = 5

    # --- Speech Similarity Search Configuration ---
    SPEECH_SIMILARITY_EMBD_MODEL: str = "openai/whisper-large-v3"
    TRANSCRIPT_SIMILARITY_EMBD_MODEL: str = "intfloat/e5-large-v2"

    # --- Image Similarity Search Configuration ---
    IMAGE_SIMILARITY_EMBD_MODEL: str = "openai/clip-vit-base-patch32"

    # --- Caption Similarity Search Configuration ---
    CAPTION_MODEL_PROMPT: str = "Describe, with high detail, every object, person, action and scenes displayed in the image."
    CAPTION_SIMILARITY_EMBD_MODEL: str = "openai/clip-vit-base-patch32"
    DELTA_SECONDS_FRAME_INTERVAL: float = 3.0

    # --- Video Search Engine Configuration ---
    VIDEO_CLIP_SPEECH_SEARCH_TOP_K: int = 1
    VIDEO_CLIP_CAPTION_SEARCH_TOP_K: int = 1
    VIDEO_CLIP_IMAGE_SEARCH_TOP_K: int = 1
    QUESTION_ANSWER_TOP_K: int = 3


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Get the application settings.

    Returns:
        Settings: The application settings.
    """
    return Settings()
