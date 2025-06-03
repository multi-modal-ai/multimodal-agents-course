import uuid
from typing import Optional

import av
import numpy as np
import pandas as pd
from moviepy import VideoFileClip
from PIL import Image


def extract_video_clip(
    video_path: str, start_time: float, end_time: float, output_path: str = None
) -> VideoFileClip:
    if start_time >= end_time:
        raise ValueError("start_time must be less than end_time")

    video = VideoFileClip(video_path)
    clip = video.subclipped(start_time=start_time, end_time=end_time)

    if output_path:
        clip.write_videofile(output_path)

    return VideoFileClip(output_path)


def create_video_from_dataframe(df: pd.DataFrame, output_path: str, fps: int = 10):
    """
    Creates a video from a DataFrame where each row contains a PIL Image
    in the specified 'frame_column'.

    Args:
        df (pd.DataFrame): DataFrame containing the image frames.
        output_path (str): Path to save the output video file (e.g., 'output.mp4').
        fps (int): Frames per second for the output video.
        frame_column (str): Name of the column containing the PIL Image objects.
    """
    container: Optional[av.container.OutputContainer] = None
    stream: Optional[av.video.stream.VideoStream] = None

    try:
        if df.empty:
            return

        first_frame: Image.Image = df.iloc[0]["frame"]
        height, width = first_frame.height, first_frame.width
        output_path = output_path / uuid.uuid4().hex / "clip.mp4"
        container = av.open(output_path, mode="w")
        stream = container.add_stream("h264", rate=fps)
        stream.pix_fmt = "yuv420p"
        stream.width = width
        stream.height = height

        for _, row in df.iterrows():
            frame: Image.Image = row["frame"]
            if frame:
                av_frame = av.VideoFrame.from_ndarray(
                    np.array(frame.convert("RGB")), format="rgb24"
                )
                for packet in stream.encode(av_frame):
                    container.mux(packet)

        for packet in stream.encode():
            container.mux(packet)

    finally:
        if container:
            container.close()
