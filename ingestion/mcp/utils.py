from pathlib import Path

import av
import numpy as np


def create_video_from_dataframe(video_df, output_path: str, fps: int) -> str:
    """Create a video from a dataframe of frames.

    Args:
        video_df: The dataframe containing the frames.
        output_path: The path to save the video.

    Returns:
        The path to the created video.
    """
    out_file = Path(output_path)
    container = av.open(str(out_file), mode="w")
    stream = container.add_stream("h264", rate=fps)
    stream.pix_fmt = "yuv420p"
    is_first_frame = True
    for frame in video_df["frame"]:
        if is_first_frame:
            stream.width = frame.width
            stream.height = frame.height
            is_first_frame = False
        else:
            if stream.width != frame.width or stream.height != frame.height:
                raise ValueError("All frames must have the same dimensions.")

    av_frame = av.VideoFrame.from_ndarray(np.array(frame.convert("RGB")), format="rgb24")
    for packet in stream.encode(av_frame):
        container.mux(packet)

    container.close()
    return str(out_file)
