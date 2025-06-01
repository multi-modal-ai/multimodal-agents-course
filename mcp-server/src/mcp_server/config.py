from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )

    # --- GROQ Configuration ---
    GROQ_API_KEY: str
    GROQ_VLM_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"

    # --- Video Ingestion Configuration ---
    VIDEO_CLIP_LENGTH = 60
    SPLIT_FPS = 1
    AUDIO_CHUNK_LENGTH = 30

    # --- Speech Similarity Search Configuration ---
    SPEECH_SIMILARITY_SEARCH_TOP_K = 3

    # --- Image Similarity Search Configuration ---
    IMAGE_SIMILARITY_SEARCH_TOP_K = 3

    # --- Caption Similarity Search Configuration ---
    CAPTION_SIMILARITY_SEARCH_TOP_K = 3


settings = Settings()
