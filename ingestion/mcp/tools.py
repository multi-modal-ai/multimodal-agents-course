import uuid

import tqdm
from core import splitter
from core.models import CachedTable
from core.video_processor import VideoProcessor, get_registry, get_table
from utils import create_video_from_dataframe

video_processor = VideoProcessor(video_clip_length=60, split_fps=1.0, audio_chunk_length=30)


def add_video(video_name: str) -> None:
    """Add a video to the pixel table.

    Args:
        video_path: The path to the video file.
        video_name: The name of the video to be added.
    """
    _cache_path = uuid.uuid4().hex
    video_clips = splitter._preprocess_video(
        video_path=video_name,
        chunk_duration=60,
        videos_cache=f".cache/{_cache_path}",
    )

    video_processor.setup_table(_cache_path, video_name)
    for video_clip in tqdm.tqdm(video_clips, desc="Adding video clips"):
        video_processor.add_video(video_clip)


def get_clips(video_name: str, user_query: str, top_k: int = 3) -> str:
    """Get a video clip based on the user query.

    Args:
        user_query: The user query to search for.

    Returns:
        The path to the video clip.
    """
    video_index: CachedTable = get_table(video_name)
    if not video_index:
        raise ValueError(f"Video index {video_name} not found in registry.")

    sims = video_index.audio_chunks_view.text.similarity(user_query)
    results = (
        video_index.sentences_view.select(
            video_index.audio_chunks_view.pos,
            video_index.audio_chunks_view.start_time_sec,
            video_index.audio_chunks_view.end_time_sec,
            similarity=sims,
        )
        .order_by(sims, asc=False)
        .limit(top_k)
        .collect()
    )

    top_k_entries = results.limit(top_k).collect()
    if len(top_k_entries) > 0:
        for entry in top_k_entries:
            start_time_sec = float(entry["start_time_sec"])
            end_time_sec = float(entry["end_time_sec"])

            sampled_frames = (
                video_index.frames_view.select(
                    video_index.frames_view.frame_idx,
                    video_index.frames_view.frame,
                )
                .where(
                    (video_index.frames_view.pos_msec >= start_time_sec * 1e3)
                    & (video_index.frames_view.pos_msec <= end_time_sec * 1e3)
                )
                .collect()
            )
            clip_path = create_video_from_dataframe(sampled_frames, output_path=video_index.video_cache)
    return clip_path


def list_tables() -> str:
    """List all video indexes currently available.

    Returns:
        A string listing the current video indexes.
    """
    keys = list(get_registry().keys())
    if not keys:
        return "No video indexes exist."
    return f"Current video indexes: {', '.join(keys)}"
