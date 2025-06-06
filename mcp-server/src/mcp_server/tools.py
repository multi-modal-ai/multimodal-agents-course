from typing import Dict
from uuid import uuid4

from loguru import logger

from mcp_server.config import get_settings
from mcp_server.video.ingestion.models import Base64Image
from mcp_server.video.ingestion.tools import extract_video_clip
from mcp_server.video.ingestion.video_processor import VideoProcessor
from mcp_server.video.video_search_engine import VideoSearchEngine

settings = get_settings()
logger = logger.bind(name="MCPVideoTools")


def process_video(video_path: str) -> str:
    """Process a video file and prepare it for searching.

    Args:
        video_path (str): Path to the video file to process.

    Returns:
        str: Success message indicating the video was processed.

    Raises:
        ValueError: If the video file cannot be found or processed.
    """
    video_processor = VideoProcessor(
        video_clip_length=settings.VIDEO_CLIP_LENGTH,
        split_fps=settings.SPLIT_FPS,
        audio_chunk_length=settings.AUDIO_CHUNK_LENGTH,
    )
    video_processor.setup_table(video_name=video_path)
    video_processor.add_video(video_path=video_path)
    return "Video processed successfully"


def get_video_clip_from_user_query(video_name: str, user_query: str) -> Dict[str, str]:
    """Get a video clip based on the user query using speech and caption similarity.

    Args:
        video_name (str): The name of the video index.
        user_query (str): The user query to search for.

    Returns:
        Dict[str, str]: Dictionary containing:
            filename (str): Path to the extracted video clip.
    """
    search_engine = VideoSearchEngine(video_name)

    speech_clips = search_engine.search_by_speech(
        user_query, settings.VIDEO_CLIP_SPEECH_SEARCH_TOP_K
    )
    caption_clips = search_engine.search_by_caption(
        user_query, settings.VIDEO_CLIP_CAPTION_SEARCH_TOP_K
    )

    speech_sim = speech_clips[0]["similarity"] if speech_clips else 0
    caption_sim = caption_clips[0]["similarity"] if caption_clips else 0

    video_clip_info = speech_clips[0] if speech_sim > caption_sim else caption_clips[0]

    video_clip = extract_video_clip(
        video_path=video_name,
        start_time=video_clip_info["start_time"],
        end_time=video_clip_info["end_time"],
        output_path=f"./videos/{str(uuid4())}.mp4",
    )

    return {"filename": video_clip.filename}


def get_video_clip_from_image(
    video_name: str, user_image: Base64Image
) -> Dict[str, str]:
    """Get a video clip based on similarity to a provided image.

    Args:
        video_name (str): The name of the video index to search in.
        user_image (Base64Image): The query image encoded in base64 format.

    Returns:
        Dict[str, str]: Dictionary containing:
            filename (str): Path to the extracted video clip.
    """
    search_engine = VideoSearchEngine(video_name)
    image_clips = search_engine.search_by_image(
        user_image, settings.VIDEO_CLIP_IMAGE_SEARCH_TOP_K
    )

    video_clip = extract_video_clip(
        video_path=video_name,
        start_time=image_clips[0]["start_time"],
        end_time=image_clips[0]["end_time"],
        output_path=f"./videos/{str(uuid4())}.mp4",
    )

    return {"filename": video_clip.filename}


def ask_question_about_video(video_name: str, user_query: str) -> Dict[str, str]:
    """Get relevant captions from the video based on the user's question.

    Args:
        video_name (str): The name of the video index to search in.
        user_query (str): The question to search for relevant captions.

    Returns:
        Dict[str, str]: Dictionary containing:
            answer (str): Concatenated relevant captions from the video.
    """
    search_engine = VideoSearchEngine(video_name)
    caption_info = search_engine.get_caption_info(
        user_query, settings.QUESTION_ANSWER_TOP_K
    )

    answer = "\n".join(entry["caption"] for entry in caption_info)
    return {"answer": answer}
