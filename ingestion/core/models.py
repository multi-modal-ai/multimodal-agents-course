import pixeltable as pxt
from pydantic import BaseModel, Field


class CachedTableMetadata(BaseModel):
    video_cache: str = Field(..., description="Path to the video cache")
    video_table: str = Field(..., description="Root video table")
    frames_view: str = Field(..., description="Video frames which were split using a FPS and frame iterator")
    sentences_view: str = Field(
        ..., description="After chunking audio, getting transcript and splitting it into sentences"
    )
    audio_chunks_view: str = Field(
        ..., description="After chunking audio, getting transcript and splitting it into sentences"
    )


class CachedTable:
    video_cache: str = Field(..., description="Path to the video cache")
    video_table: pxt.Table = Field(..., description="Root video table")
    frames_view: pxt.Table = Field(..., description="Video frames which were split using a FPS and frame iterator")
    sentences_view: pxt.Table = Field(
        ..., description="After chunking audio, getting transcript and splitting it into sentences"
    )
    audio_chunks_view: pxt.Table = Field(
        ..., description="After chunking audio, getting transcript and splitting it into sentences"
    )

    def __init__(
        self,
        video_cache: str,
        video_table: pxt.Table,
        frames_view: pxt.Table,
        sentences_view: pxt.Table,
        audio_chunks_view: pxt.Table,
    ):
        self.video_cache = video_cache
        self.video_table = video_table
        self.frames_view = frames_view
        self.sentences_view = sentences_view
        self.audio_chunks_view = audio_chunks_view

    @classmethod
    def from_metadata(cls, metadata: CachedTableMetadata) -> "CachedTable":
        return cls(
            video_cache=metadata.video_cache,
            video_table=pxt.get_table(metadata.video_table),
            frames_view=pxt.get_table(metadata.frames_view),
            audio_chunks_view=pxt.get_table(metadata.audio_chunks_view),
            sentences_view=pxt.get_table(metadata.sentences_view),
        )

    def __str__(self):
        return {
            "video_cache": self.video_cache,
            "video_table": str(self.video_table),
            "frames_view": str(self.frames_view),
            "audio_chunks_view": str(self.audio_chunks_view),
            "sentences_view": str(self.sentences_view),
        }
