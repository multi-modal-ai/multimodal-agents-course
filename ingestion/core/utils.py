from typing import Optional

import av
import numpy as np
import pandas as pd
from PIL import Image


def create_video_from_dataframe(df: pd.DataFrame, output_path: str, fps: int = 25, frame_column: str = "frame"):
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

        first_frame: Image.Image = df.iloc[0][frame_column]
        height, width = first_frame.height, first_frame.width

        container = av.open(output_path, mode="w")
        stream = container.add_stream("h264", rate=fps)
        stream.pix_fmt = "yuv420p"
        stream.width = width
        stream.height = height

        for _, row in df.iterrows():
            frame: Image.Image = row[frame_column]
            if frame:
                av_frame = av.VideoFrame.from_ndarray(np.array(frame.convert("RGB")), format="rgb24")
                for packet in stream.encode(av_frame):
                    container.mux(packet)

        for packet in stream.encode():
            container.mux(packet)

    finally:
        if container:
            container.close()
