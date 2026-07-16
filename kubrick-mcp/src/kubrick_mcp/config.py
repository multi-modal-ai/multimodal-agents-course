from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="kubrick-mcp/.env", extra="ignore", env_file_encoding="utf-8")

    # --- OPIK Configuration ---
    OPIK_API_KEY: str
    OPIK_WORKSPACE: str = "default"
    OPIK_PROJECT: str = "kubrick-mcp"

    # --- OPENAI Configuration ---
    OPENAI_API_KEY: str
    AUDIO_TRANSCRIPT_MODEL: str = "gpt-4o-mini-transcribe"  # Whisper tiny model 37M
    IMAGE_CAPTION_MODEL: str = "gpt-4o-mini"

    # --- Video Understanding Configuration ---
    MINIMAX_API_KEY: str | None = None
    MINIMAX_REGION: Literal["global_en", "cn_zh"] = "global_en"
    MINIMAX_PROTOCOL: Literal["openai", "anthropic"] = "anthropic"
    MINIMAX_VIDEO_MODEL: str = "MiniMax-M3"
    MINIMAX_THINKING: Literal["adaptive", "disabled"] = "adaptive"
    MINIMAX_MAX_COMPLETION_TOKENS: int = 4096
    MINIMAX_REQUEST_TIMEOUT_SECONDS: float = 120.0
    MINIMAX_OPENAI_BASE_URL_GLOBAL: str = "https://api.minimax.io/v1"
    MINIMAX_ANTHROPIC_BASE_URL_GLOBAL: str = "https://api.minimax.io/anthropic"
    MINIMAX_OPENAI_BASE_URL_CN: str = "https://api.minimaxi.com/v1"
    MINIMAX_ANTHROPIC_BASE_URL_CN: str = "https://api.minimaxi.com/anthropic"

    # --- Video Ingestion Configuration ---
    SPLIT_FRAMES_COUNT: int = 45
    AUDIO_CHUNK_LENGTH: int = 10
    AUDIO_OVERLAP_SECONDS: int = 1
    AUDIO_MIN_CHUNK_DURATION_SECONDS: int = 1

    # --- Transcription Similarity Search Configuration ---
    TRANSCRIPT_SIMILARITY_EMBD_MODEL: str = "text-embedding-3-small"

    # --- Image Similarity Search Configuration ---
    IMAGE_SIMILARITY_EMBD_MODEL: str = "openai/clip-vit-base-patch32"

    # --- Image Captioning Configuration ---
    IMAGE_RESIZE_WIDTH: int = 1024
    IMAGE_RESIZE_HEIGHT: int = 768
    CAPTION_SIMILARITY_EMBD_MODEL: str = "text-embedding-3-small"

    # --- Caption Similarity Search Configuration ---
    CAPTION_MODEL_PROMPT: str = "Describe what is happening in the image"
    DELTA_SECONDS_FRAME_INTERVAL: float = 5.0

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
