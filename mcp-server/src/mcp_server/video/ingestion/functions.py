from loguru import logger
import pixeltable as pxt
from groq import RateLimitError

from mcp_server.video.ingestion.caption import VisualCaptioningModel

video_captioner = VisualCaptioningModel()

# TODO: Here, add some internal batching logic to avoid rate limit erros
@pxt.udf
async def caption_image(
    image: pxt.type_system.Image, prompt: pxt.type_system.String
) -> str:
    try:
        im_caption = await video_captioner.caption(image, prompt)
        return im_caption
    except RateLimitError as e:
        logger.error(f"Rate limit error after exponential backoff: {e}")
        return ""
    except Exception as e:
        logger.error(f"Error captioning image: {e}")
        return ""


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
