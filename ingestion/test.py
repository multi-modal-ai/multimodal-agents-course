if __name__ == "__main__":
    video_path = "/home/razvantalexandru/Documents/Projects/NeuralBits/multimodal-agents-course/.cache/por_vs_esp_5min/2018_portugal_vs_spain_T0h0m_0h5m.mp4"
    from core.video_processor import VideoProcessor

    video_processor = VideoProcessor(video_clip_length=60, split_fps=1.0, audio_chunk_length=30)
    video_processor.setup_table(video_name=video_path)
    video_processor.add_video(video_path=video_path)
    print(f"Video {video_path} added successfully.")
