from core.video_processor import VideoProcessor

if __name__ == "__main__":
    video_path = "data/long_video/2018_portugal_vs_spain_T0h0m_0h5m.mp4"
    cache_path = ".cache/por_vs_esp_5min"
    video_processor = VideoProcessor(pxt_cache="poc", videos_cache=cache_path)
    video_processor.compose_pixeltable()

    cache_path, video_clips = video_processor.preprocess_video(video_path=video_path, chunk_duration=60)
    # FIXME: move these to config file
    try:
        for clip in video_clips:
            video_processor.add_video(clip)
    except Exception as e:
        print(f"Error adding video: {e}")
