import base64
import io
from typing import List, Literal, Union

import pixeltable as pxt
from PIL import Image
from pydantic import BaseModel, Field, field_validator

#####################################
# Table Registry Models
#####################################


class CachedTableMetadata(BaseModel):
    video_cache: str = Field(..., description="Path to the video cache")
    video_table: str = Field(..., description="Root video table")
    frames_view: str = Field(
        ..., description="Video frames which were split using a FPS and frame iterator"
    )
    audio_chunks_view: str = Field(
        ...,
        description="After chunking audio, getting transcript and splitting it into sentences",
    )


class CachedTable:
    video_cache: str = Field(..., description="Path to the video cache")
    video_table: pxt.Table = Field(..., description="Root video table")
    frames_view: pxt.Table = Field(
        ..., description="Video frames which were split using a FPS and frame iterator"
    )
    audio_chunks_view: pxt.Table = Field(
        ...,
        description="After chunking audio, getting transcript and splitting it into sentences",
    )

    def __init__(
        self,
        video_cache: str,
        video_table: pxt.Table,
        frames_view: pxt.Table,
        audio_chunks_view: pxt.Table,
    ):
        self.video_cache = video_cache
        self.video_table = video_table
        self.frames_view = frames_view
        self.audio_chunks_view = audio_chunks_view

    @classmethod
    def from_metadata(cls, metadata: dict | CachedTableMetadata) -> "CachedTable":
        metadata = (
            CachedTableMetadata(**metadata) if isinstance(metadata, dict) else metadata
        )
        return cls(
            video_cache=metadata.video_cache,
            video_table=pxt.get_table(metadata.video_table),
            frames_view=pxt.get_table(metadata.frames_view),
            audio_chunks_view=pxt.get_table(metadata.audio_chunks_view),
        )

    def __str__(self):
        return {
            "video_cache": self.video_cache,
            "video_table": str(self.video_table),
            "frames_view": str(self.frames_view),
            "audio_chunks_view": str(self.audio_chunks_view),
        }


######################################
# Image Processing Models
######################################


class Base64Image(BaseModel):
    image: str = Field(description="Base64 encoded image string")

    @field_validator("image", mode="before")
    def encode_image(cls, v):
        if isinstance(v, Image.Image):
            buffered = io.BytesIO()
            v.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
        return v

    def to_pil(self) -> Image.Image:
        return Image.open(io.BytesIO(base64.b64decode(self.image)))


class TextContent(BaseModel):
    type: Literal["text"] = "text"
    text: str


class ImageUrlContent(BaseModel):
    type: Literal["image_url"] = "image_url"
    base64_image: str = Field(..., serialization_alias="image_url")

    @field_validator("base64_image", mode="before")
    def serialize_image(cls, v):
        if isinstance(v, str):
            return f"data:image/jpeg;base64,{v}"
        raise TypeError("image_url must be a dict with 'url' or a PIL Image")


class UserContent(BaseModel):
    role: Literal["user"] = "user"
    content: List[Union[TextContent, ImageUrlContent]]

    @classmethod
    def from_pair(cls, base64_image: str, prompt: str):
        return cls(
            content=[
                TextContent(text=prompt),
                ImageUrlContent(base64_image=base64_image),
            ]
        )
