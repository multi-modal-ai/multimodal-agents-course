import glob
import os
import subprocess
from pathlib import Path
from typing import List


def split_video_to_chunks_subprocess(
    video_path: Path,
    chunk_duration=60,
    cache_path: Path = Path(os.getcwd()) / ".cache/tmp",
):
    # Add docs to this func, currently splits in 1min chunks
    try:
        probe_command = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path,
        ]
        process = subprocess.run(probe_command, capture_output=True, text=True, check=True)
        duration = float(process.stdout.strip())
        num_segments = int(duration // chunk_duration) + (1 if duration % chunk_duration > 0 else 0)
        cache_path = Path(cache_path) / f"video_chunks_ffmpeg_splits{chunk_duration}_{video_path.stem}"

        if cache_path.exists():
            return cache_path
        cache_path.mkdir(parents=True, exist_ok=True)

        for i in range(num_segments):
            start_time = i * chunk_duration
            output_file = os.path.join(cache_path, f"chunk_{i:03d}.mp4")
            # NOTE:
            # this is equiv to ffmpeg -i video.mp4 -ss 00:00:00 -t 00:01:00 -c copy output.mp4
            # -c copy does faster re-encoding than inline as it copies channel only
            ffmpeg_command = [
                "ffmpeg",
                "-i",
                video_path,
                "-ss",
                str(start_time),
                "-t",
                str(chunk_duration),
                "-avoid_negative_ts",
                "make_zero",
                "-c",
                "copy",
                output_file,
            ]
            subprocess.run(ffmpeg_command, check=True, capture_output=True)
        return cache_path

    # FIXME: solve prints to logger
    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg: {e.stderr.decode('utf8')}")
        return None
    except FileNotFoundError:
        print("Error: ffmpeg or ffprobe not found. Make sure they are installed and in your system's PATH.")
        return None
    except ValueError:
        print("Error: Could not parse video duration.")
        return None


def _preprocess_video(
    video_path: str,
    chunk_duration: int = 60,
    videos_cache: str = ".cache",
) -> List[Path]:
    """Preprocess the video and split it into chunks.

    Args:
        video_path: The path to the video file.
        chunk_duration: The duration of each chunk in seconds.
        videos_cache: The cache directory for videos.

    Returns:
        A tuple containing the cache path and a list of video clips.
    """
    vpath = Path(video_path)
    assert vpath.exists(), f"Video could not be found {video_path}"

    video_segments_cache = split_video_to_chunks_subprocess(
        video_path=vpath,
        chunk_duration=chunk_duration,
        cache_path=videos_cache,
    )

    video_files = glob.glob(f"{str(video_segments_cache)}/*.mp4")
    video_files.sort()
    video_files = [Path(file) for file in video_files]
    return video_files


__all__ = ["split_video_to_chunks_subprocess", "_preprocess_video"]
