import pixeltable as pxt
from pixeltable.functions import whisper
from pixeltable.functions.audio import get_metadata
from pixeltable.functions.video import make_video
from pixeltable.iterators import FrameIterator
from transformers import BlipForConditionalGeneration, BlipProcessor

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")


@pxt.udf
def caption_frame(image_frame: pxt.type_system.Image) -> str:
    _pretext = "a photography of"
    inputs = processor(image_frame, _pretext, return_tensors="pt")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)

    return caption


if __name__ == "__main__":
    video_clips = (
        "/Users/razvantalexandru/Documents/NeuralBits/multimodal-agents-course/.cache/por_vs_esp_5min/clip_000.mp4",
        "/Users/razvantalexandru/Documents/NeuralBits/multimodal-agents-course/.cache/por_vs_esp_5min/clip_001.mp4",
        "/Users/razvantalexandru/Documents/NeuralBits/multimodal-agents-course/.cache/por_vs_esp_5min/clip_002.mp4",
        "/Users/razvantalexandru/Documents/NeuralBits/multimodal-agents-course/.cache/por_vs_esp_5min/clip_003.mp4",
        "/Users/razvantalexandru/Documents/NeuralBits/multimodal-agents-course/.cache/por_vs_esp_5min/clip_004.mp4",
    )

    pxt.drop_dir("mm_agent_poc", force=True)
    pxt.create_dir("mm_agent_poc")

    video_table = pxt.create_table(
        "mm_agent_poc.videos",
        {
            "video": pxt.Video,
            # "frames": pxt.Array(pxt.Image),
            # "captions": pxt.Array(pxt.String),
            # "audio": pxt.Audio,
            # "transcription": pxt.String,
            # "sentences": pxt.Array(pxt.String),
        },
    )
    video_table.insert([{"video": video_clips[0]}])

    frames_view = pxt.create_view(
        "frames",
        video_table,
        iterator=FrameIterator.create(video=video_table.video, num_frames=2),
    )

    frames_view.select(frames_view.frame, caption_frame(frames_view.frame)).as_dict()

    frames_view.add_computed_column(
        caption=caption_frame(image_frame=frames_view.frame),
    )

    # video_table.add_computed_column(audio=extract_audio(video_table.video, format="mp3"), if_exists="ignore")
    # video_table.add_computed_column(transcription=whisper.transcribe(audio=video_table.audio, model="base.en"))
    # video_table.add_computed_column(metadata=get_metadata(video_table.audio))

    video_table.describe()
