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
    semantics_index: str = Field(..., description="Embedding index for the sentences")


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
    semantics_index: pxt.Table = Field(..., description="Embedding index for the sentences")

    def from_metadata(cls, metadata: CachedTableMetadata) -> "CachedTable":
        return cls(
            video_cache=metadata.video_cache,
            video_table=pxt.get_table(metadata.video_table),
            frames_view=pxt.get_table(metadata.frames_view),
            audio_chunks_view=pxt.get_table(metadata.audio_chunks_view),
            sentences_view=pxt.get_table(metadata.sentences_view),
            semantics_index=pxt.get_table(metadata.semantics_index),
        )
