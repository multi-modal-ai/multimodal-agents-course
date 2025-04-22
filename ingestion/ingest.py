from core.video_processor import VideoProcessor

if __name__ == "__main__":
    video_path = "/home/razvantalexandru/Documents/Projects/NeuralBits/multimodal-agents-course/.cache/por_vs_esp_5min/2018_portugal_vs_spain_T0h0m_0h5m.mp4"
    cache_path = "/home/razvantalexandru/Documents/Projects/NeuralBits/multimodal-agents-course/.cache/"
    video_processor = VideoProcessor(pxt_cache="poc", videos_cache=cache_path)

    cache_path, video_clips = video_processor.preprocess_video(video_path=video_path, chunk_duration=60)
    video_processor.warm_up_table(first_video=video_clips[0])

    try:
        for clip in video_clips[1:]:
            video_processor.add_video(clip)
            print("Added")
    except Exception as e:
        print(f"Error adding video: {e}")
