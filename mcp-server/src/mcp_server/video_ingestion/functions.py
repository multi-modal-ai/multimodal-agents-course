import pixeltable as pxt
from mcp_server.video_ingestion.caption import VisualCaptioningModel

visual_captioner_model = VisualCaptioningModel()


@pxt.udf
def caption_image(image: pxt.type_system.Image, prompt: pxt.type_system.String) -> str:
    return visual_captioner_model.caption(image, prompt, True)


@pxt.udf
def compose_semantics(
    video_caption: pxt.type_system.String, transcript: pxt.type_system.Json
) -> str:
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
