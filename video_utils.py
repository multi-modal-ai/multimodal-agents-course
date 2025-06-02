from moviepy.editor import VideoFileClip


def extract_video_clip(
    video_path: str, start_time: float, end_time: float, output_path: str = None
) -> VideoFileClip:
    """
    Extract a clip from a video file between specified start and end times.

    Args:
        video_path (str): Path to the input video file
        start_time (float): Start time in seconds
        end_time (float): End time in seconds
        output_path (str, optional): Path to save the output clip. If None, the clip is returned without saving.

    Returns:
        VideoFileClip: The extracted video clip

    Raises:
        FileNotFoundError: If the input video file doesn't exist
        ValueError: If start_time is greater than or equal to end_time
    """
    if start_time >= end_time:
        raise ValueError("start_time must be less than end_time")

    # Load the video
    video = VideoFileClip(video_path)

    # Extract the clip
    clip = video.subclip(start_time, end_time)

    # Save the clip if output_path is provided
    if output_path:
        clip.write_videofile(output_path)

    return clip
