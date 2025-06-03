from loguru import logger
from typing import List

from mcp_server.video_ingestion.models import Base64ToPILImageModel, CachedTable
from mcp_server.video_ingestion.video_processor import VideoProcessor, get_registry, get_table

from mcp_server.config import settings


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


def get_clip_by_speech_sim(
    video_name: str,
    user_query: str,
    top_k: int = settings.SPEECH_SIMILARITY_SEARCH_TOP_K,
) -> List[dict]:
    """Get a video clip based on the user query.

    Args:
        user_query: The user query to search for.

    Returns:
        The path to the video clip.
    """
    video_index: CachedTable = get_table(video_name)
    if not video_index:
        raise ValueError(f"Video index {video_name} not found in registry.")

    sims = video_index.audio_chunks_view.chunk_text.similarity(user_query)
    results = video_index.audio_chunks_view.select(
        video_index.audio_chunks_view.pos,
        video_index.audio_chunks_view.start_time_sec,
        video_index.audio_chunks_view.end_time_sec,
        similarity=sims,
    ).order_by(sims, asc=False)
    
    video_clips = []
    top_k_entries = results.limit(top_k).collect()
    
    logger.info(top_k_entries)
    logger.info(len(top_k_entries))

    if len(top_k_entries) > 0:
        for entry in top_k_entries:
            logger.info(entry)
            video_clip_info_dict = {
                "start_time": float(entry["start_time_sec"]),
                "end_time": float(entry["end_time_sec"]),
                "similarity": float(entry["similarity"]),
            }
            video_clips.append(video_clip_info_dict)
            
    return video_clips


def get_clip_by_image_sim(
    video_name: str,
    image_base64: Base64ToPILImageModel,
    top_k: int = settings.IMAGE_SIMILARITY_SEARCH_TOP_K,
) -> List[dict]:
    """Get a video clip based on the user query using image similarity.

    Args:
        video_name: The name of the video index.
        user_query: The user query to search for.
        top_k: The number of top results to return.

    Returns:
        A string listing the paths to the video clips.
    """
    video_index: CachedTable = get_table(video_name)
    if not video_index:
        raise ValueError(f"Video index {video_name} not found in registry.")

    sims = video_index.frames_view.image.similarity(image_base64.get_image())
    results = video_index.frames_view.select(
        video_index.frames_view.pos_msec,
        video_index.frames_view.frame,
        similarity=sims,
    ).order_by(sims, asc=False)

    video_clips = []
    top_k_entries = results.limit(top_k).collect()
    if len(top_k_entries) > 0:
        for entry in top_k_entries:
            video_clip_info_dict = {
                "start_time": entry["pos_msec"] / 1000. - settings.DELTA_SECONDS_FRAME_INTERVAL ,
                "end_time": entry["pos_msec"] / 1000. + settings.DELTA_SECONDS_FRAME_INTERVAL,
                "similarity": float(entry["similarity"]),
            }
            video_clips.append(video_clip_info_dict)
    return video_clips


def get_clip_by_caption_sim(
    video_name: str,
    user_query: str,
    top_k: int = settings.CAPTION_SIMILARITY_SEARCH_TOP_K,
) -> List[dict]:
    """Get a video clip based on the user query using caption similarity.

    Args:
        video_name: The name of the video index.
        user_query: The user query to search for.
        top_k: The number of top results to return.

    Returns:
        A string listing the paths to the video clips.
    """
    video_index: CachedTable = get_table(video_name)
    if not video_index:
        raise ValueError(f"Video index {video_name} not found in registry.")

    sims = video_index.frames_view.im_caption.similarity(user_query)
    results = video_index.frames_view.select(
        video_index.frames_view.pos_msec,
        video_index.frames_view.im_caption,
        similarity=sims,
    ).order_by(sims, asc=False)

    video_clips = []
    top_k_entries = results.limit(top_k).collect()
    if len(top_k_entries) > 0:
        for entry in top_k_entries:
            video_clip_info_dict = {
                "start_time": entry["pos_msec"] / 1000. - settings.DELTA_SECONDS_FRAME_INTERVAL ,
                "end_time": entry["pos_msec"] / 1000. + settings.DELTA_SECONDS_FRAME_INTERVAL,
                "similarity": float(entry["similarity"]),
            }
            video_clips.append(video_clip_info_dict)
    return video_clips


def list_tables() -> str:
    """List all video indexes currently available.

    Returns:
        A string listing the current video indexes.
    """
    keys = list(get_registry().keys())
    if not keys:
        return "No video indexes exist."
    return f"Current video indexes: {', '.join(keys)}"
