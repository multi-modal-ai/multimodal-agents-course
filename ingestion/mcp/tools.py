import os

from core.models import Base64ToPILImageModel, CachedTable
from core.video_processor import VideoProcessor, get_registry, get_table
from pixeltable.functions.video import make_video

video_processor = VideoProcessor(video_clip_length=60, split_fps=1.0, audio_chunk_length=30)


def add_video(video_name: str) -> None:
    """Add a video to the pixel table.

    Args:
        video_path: The path to the video file.
        video_name: The name of the video to be added.
    """
    table_name = video_name.split(os.sep)[-1].split(os.extsep)[0]
    video_processor.setup_table(video_name=table_name)
    video_processor.add_video(video_path=str(video_name))


def get_clip_by_speech_sim(video_name: str, user_query: str, top_k: int = 3) -> str:
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
    if len(top_k_entries) > 0:
        for entry in top_k_entries:
            start_time_sec = float(entry["start_time_sec"])
            end_time_sec = float(entry["end_time_sec"])

            sampled_clip = video_index.frames_view.select(make_video(video_index.frames_view.frame)).where(
                (video_index.frames_view.pos_msec >= start_time_sec * 1e3)
                & (video_index.frames_view.pos_msec <= end_time_sec * 1e3)
            )
            video_clips.append(sampled_clip)
    return video_clips


def get_clip_by_image_sim(video_name: str, image_base64: Base64ToPILImageModel, top_k: int = 3) -> str:
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
            pos_msec = float(entry["pos_msec"])
            sampled_clip = video_index.frames_view.select(make_video(video_index.frames_view.frame)).where(
                (video_index.frames_view.pos_msec >= pos_msec - 500)
                & (video_index.frames_view.pos_msec <= pos_msec + 500)
            )
            video_clips.append(sampled_clip)
    return video_clips


def get_clip_by_caption_sim(video_name: str, user_query: str, top_k: int = 3) -> str:
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
            pos_msec = float(entry["pos_msec"])
            sampled_clip = video_index.frames_view.select(make_video(video_index.frames_view.frame)).where(
                (video_index.frames_view.pos_msec >= pos_msec - 500)
                & (video_index.frames_view.pos_msec <= pos_msec + 500)
            )
            video_clips.append(sampled_clip)
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
