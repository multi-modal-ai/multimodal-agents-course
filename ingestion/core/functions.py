from pathlib import Path

import pixeltable as pxt
from core.caption import VisualCaptioningModel

video_captioner = VisualCaptioningModel(device="cuda")


@pxt.udf
def caption_video(video: pxt.type_system.Video, prompt: pxt.type_system.String) -> str:
    vpath = Path(video)
    assert vpath.exists(), f"Video {video} invalid!"
    preprocessed = video_captioner.preprocess_video(video_path=video, prompt=prompt)
    generation = video_captioner(preprocessed)
    return str(generation[-1])


@pxt.udf
def compose_semantics(video_caption: pxt.type_system.String, transcript: pxt.type_system.Json) -> str:
    return f"{video_caption}.{transcript['text']}"
