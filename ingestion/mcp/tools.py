import uuid

import tqdm
from core import splitter
from core.models import CachedTable
from core.video_processor import VideoProcessor, get_registry, get_table
from fastmcp import FastMCP

from ingestion.core import tools

video_processor = VideoProcessor(video_clip_length=60, split_fps=1.0, audio_chunk_length=30)

mcp = FastMCP("VideoProcessor")


@mcp.tool(
    name="add_video",
    description="Add a new video to database.",
    tags=["video", "ingestion"],
)
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


@mcp.tool(
    name="fetch_clip",
    description="Fetch a video clip based on a user query.",
    tags=["video", "query"],
)
def get_clips(video_name: str, user_query: str, top_k: int = 1) -> str:
    """Get a video clip based on the user query.

    Args:
        user_query: The user query to search for.

    Returns:
        The path to the video clip.
    """
    video_index: CachedTable = get_table(video_name)
    if not video_index:
        raise ValueError(f"Video index {video_name} not found in registry.")

    sims = video_index.sentences_view.text.similarity(user_query)
    results_df = (
        video_index.sentences_view.select(
            video_index.sentences_view.pos,
            video_index.sentences_view.start_time_sec,
            video_index.sentences_view.end_time_sec,
            similarity=sims,
        )
        .order_by(sims, asc=False)
        .limit(top_k)
        .collect()
        .to_pandas()
    )

    best_entry_index = results_df["similarity"].idxmax()
    best_start_time = results_df.loc[best_entry_index, "start_time_sec"]
    best_end_time = results_df.loc[best_entry_index, "end_time_sec"]

    frames = (
        video_index.frames_view.select(
            video_index.frames_view.frame,
        )
        .where(
            (video_index.frames_view.pos_msec >= best_start_time * 1e3)
            & (video_index.frames_view.pos_msec <= best_end_time * 1e3)
        )
        .order_by(video_index.frames_view.frame_idx)
    )

    frames_df = frames.collect().to_pandas()
    clip_path = tools.create_video_from_dataframe(frames_df, output_path=video_index.video_cache)
    return clip_path


@mcp.tool(
    name="list_videos",
    description="List all processed videos in database.",
    tags=["video", "list"],
)
def list_tables() -> str:
    """List all video indexes currently available.

    Returns:
        A string listing the current video indexes.
    """
    keys = list(get_registry().keys())
    if not keys:
        return "No video indexes exist."
    return f"Current video indexes: {', '.join(keys)}"
