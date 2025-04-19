from core.video_processor import VideoProcessor

if __name__ == "__main__":
    video_path = "/home/razvantalexandru/Documents/Projects/NeuralBits/multimodal-agents-course/.cache/por_vs_esp_5min/2018_portugal_vs_spain_T0h0m_0h5m.mp4"
    video_processor = VideoProcessor()

    video_processor.prepare_table_schema()
    video_clips = video_processor.preprocess_video(video_path=video_path)

    for clip in video_clips:
        video_processor.add_video(clip)
        print("Added")

    print("Done")
