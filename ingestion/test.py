import time

import pixeltable as pxt
from pixeltable.functions import whisper
from pixeltable.functions.audio import get_metadata
from pixeltable.functions.video import extract_audio
from pixeltable.iterators import FrameIterator

if __name__ == "__main__":
    # video_path = "/Users/razvantalexandru/Documents/NeuralBits/multimodal-agents-course/.cache/FULL MATCH： Portugal v Spain ｜ 2018 FIFA World Cup [OFbyNU6UQQs].webm"
    video_path = (
        "/Users/razvantalexandru/Documents/NeuralBits/multimodal-agents-course/.cache/portugal_vs_spain_15m.mp4"
    )
    pxt.drop_dir("demo", force=True)
    pxt.create_dir("demo")

    video_table = pxt.create_table("demo.videos", {"video": pxt.Video})
    st = time.time()
    video_table.insert([{"video": video_path}])
    en = time.time() - st
    print(f"Time to insert video: {en:.2f} seconds")

    frames_view = pxt.create_view(
        "frames_view",
        video_table,
        iterator=FrameIterator.create(
            video=video_table.video,
            num_frames=2500,
        ),
    )

    video_table.add_computed_column(audio=extract_audio(video_table.video, format="mp3"), if_exists="ignore")
    video_table.add_computed_column(transcription=whisper.transcribe(audio=video_table.audio, model="base.en"))
    video_table.add_computed_column(metadata=get_metadata(video_table.audio))

    video_table.show()
