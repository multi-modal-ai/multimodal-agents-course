from pathlib import Path

import pixeltable as pxt
from core.caption import CaptionModelType, VisualCaptioningModel

video_captioner = VisualCaptioningModel(device="cuda", model_tag=CaptionModelType.Qwen25_3B)


@pxt.udf
def caption_video(video: pxt.type_system.Video, prompt: pxt.type_system.String) -> str:
    vpath = Path(video)
    assert vpath.exists(), f"Video {video} invalid!"
    preprocessed = video_captioner.preprocess(clip_path=video, prompt=prompt)
    generation = video_captioner.infer(preprocessed)
    return str(generation[-1])


@pxt.udf
def caption_image(image: pxt.type_system.Image, prompt: pxt.type_system.String) -> str:
    preprocessed = video_captioner.preprocess(input_data=image, prompt=prompt)
    generation = video_captioner.infer(preprocessed)
    return str(generation[-1])


@pxt.udf
def compose_semantics(video_caption: pxt.type_system.String, transcript: pxt.type_system.Json) -> str:
    return f"{video_caption}.{transcript['text']}"


@pxt.udf
def extract_text_from_chunk(transcript: pxt.type_system.Json) -> str:
    return f"{transcript['text']}"


@pxt.udf
def group_sentence_by_frames(
    frame_pos_msec: pxt.type_system.Float, transcript: pxt.type_system.Json
) -> pxt.type_system.String:
    relevant_text = ""
    frame_start_time = frame_pos_msec / 1e3
    frame_end_time = frame_pos_msec / 1e3 + 1

    for segment in transcript["segments"]:
        segment_start = segment["start"]
        segment_end = segment["end"]

        if segment_start < frame_end_time and segment_end > frame_start_time:
            relevant_text += segment["text"] + " "

    return relevant_text.strip()
