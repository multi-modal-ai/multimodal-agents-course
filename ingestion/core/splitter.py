import os
import subprocess
import tempfile


def split_video_to_chunks_subprocess(video_path, chunk_duration=60):
    """
    Splits a long video into chunks of specified duration using ffmpeg as a subprocess
    and saves them in a temporary directory.

    Args:
        video_path (str): The path to the input video file.
        chunk_duration (int): The duration of each chunk in seconds (default is 60 seconds).

    Returns:
        str: The path to the temporary directory where the video chunks are saved.
             Returns None if an error occurs.
    """
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

        temp_dir = tempfile.mkdtemp(prefix="video_chunks_ffmpeg_sub_")

        for i in range(num_segments):
            start_time = i * chunk_duration
            output_file = os.path.join(temp_dir, f"chunk_{i:03d}.mp4")
            ffmpeg_command = [
                "ffmpeg",
                "-i",
                video_path,
                "-ss",
                str(start_time),
                "-t",
                str(chunk_duration),
                "-c",
                "copy",  # Use 'copy' for faster re-muxing if possible
                output_file,
            ]
            subprocess.run(ffmpeg_command, check=True, capture_output=True)

        return temp_dir

    except subprocess.CalledProcessError as e:
        print(f"Error running ffmpeg: {e.stderr.decode('utf8')}")
        return None
    except FileNotFoundError:
        print("Error: ffmpeg or ffprobe not found. Make sure they are installed and in your system's PATH.")
        return None
    except ValueError:
        print("Error: Could not parse video duration.")
        return None
