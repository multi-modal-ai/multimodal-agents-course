import uuid
from pathlib import Path
from typing import TYPE_CHECKING

import pixeltable as pxt
from loguru import logger
from pixeltable.functions import whisper
from pixeltable.functions.huggingface import clip, sentence_transformer
from pixeltable.functions.video import extract_audio
from pixeltable.iterators import AudioSplitter
from pixeltable.iterators.video import FrameIterator

import mcp_server.video.ingestion.registry as registry
from mcp_server.video.ingestion.functions import caption_image, extract_text_from_chunk

if TYPE_CHECKING:
    from mcp_server.video.ingestion.models import CachedTable

logger = logger.bind(name="VideoProcessor")


class VideoProcessor:
    def __init__(
        self,
        video_clip_length: int = 60,
        split_fps: float = 1.0,
        audio_chunk_length: float = 30,
    ):
        self.clip_len = video_clip_length
        self.split_fps = split_fps
        self.audio_chunk_length = audio_chunk_length
        self.pxt_cache = None

        logger.info(
            f"VideoProcessor initialized with clip length: {self.clip_len}, split fps: {self.split_fps}, audio chunk length: {self.audio_chunk_length}"
        )

    def setup_table(self, video_name: str):
        self.video_mapping_idx = video_name
        exists = self._check_if_exists()
        if exists:
            logger.info(
                f"Video index '{self.video_mapping_idx}' already exists and is ready for use."
            )
            cached_table: "CachedTable" = registry.get_table(self.video_mapping_idx)
            self.pxt_cache = cached_table.video_cache
            self.video_table = cached_table.video_table
            self.frames_view = cached_table.frames_view
            self.audio_chunks = cached_table.audio_chunks_view

        else:
            self.pxt_cache = f"cache_{uuid.uuid4().hex[-4:]}"
            self.video_table_name = f"{self.pxt_cache}.table"
            self.frames_view_name = f"{self.video_table_name}_frames"
            self.audio_view_name = f"{self.video_table_name}_audio_chunks"
            self.video_table = None

            self._setup_table()

            registry.add_index_to_registry(
                video_name=self.video_mapping_idx,
                video_cache=self.pxt_cache,
                frames_view_name=self.frames_view_name,
                audio_view_name=self.audio_view_name,
            )
            logger.info(
                f"Creating new video index '{self.video_table_name}' in '{self.pxt_cache}'"
            )

    def _check_if_exists(self) -> bool:
        """
        Checks if the PixelTable table and related views/index for the video index exist.

        Returns:
            bool: True if all components exist, False otherwise.
        """
        existing_tables = registry.get_registry()
        return self.video_mapping_idx in existing_tables

    def _setup_table(self):
        logger.info(f"Creating cache path {self.pxt_cache}.")
        Path(self.pxt_cache).mkdir(parents=True, exist_ok=True)
        pxt.create_dir(self.pxt_cache, if_exists="replace_force")

        self.video_table = pxt.create_table(
            self.video_table_name,
            schema={"video": pxt.Video},
            if_exists="replace_force",
        )

        self.video_table.add_computed_column(
            audio_extract=extract_audio(self.video_table.video, format="mp3"),
            if_exists="ignore",
        )

        self.audio_chunks = pxt.create_view(
            self.audio_view_name,
            self.video_table,
            iterator=AudioSplitter.create(
                audio=self.video_table.audio_extract,
                chunk_duration_sec=5.0,
                overlap_sec=1.0,
                min_chunk_duration_sec=5.0,
            ),
            if_exists="ignore",
        )

        self.audio_chunks.add_computed_column(
            transcription=whisper.transcribe(
                audio=self.audio_chunks.audio_chunk, model="base.en"
            ),
            if_exists="ignore",
        )
        self.audio_chunks.add_computed_column(
            chunk_text=extract_text_from_chunk(self.audio_chunks.transcription),
            if_exists="ignore",
        )

        self.audio_chunks.add_embedding_index(
            column=self.audio_chunks.chunk_text,
            string_embed=sentence_transformer.using(model_id="intfloat/e5-large-v2"),
            if_exists="ignore",
            idx_name="chunks_index",
        )

        self.frames_view = pxt.create_view(
            self.frames_view_name,
            self.video_table,
            iterator=FrameIterator.create(
                video=self.video_table.video, fps=0.5
            ),  # FIXME: move to config
            if_exists="ignore",
        )

        # Add semantic index for raw frames and over their captions using the same CLIP model
        # CLIP is contrastive, embeddings of text-image pairs are close in the embedding space
        self.frames_view.add_embedding_index(
            column=self.frames_view.frame,
            image_embed=clip.using(model_id="openai/clip-vit-base-patch32"),
        )

        self.frames_view.add_computed_column(
            im_caption=caption_image(
                image=self.frames_view.frame,
                prompt="Explain in detail everything you see in the image.",  # FIXME: move to config
            ),
            if_exists="ignore",
        )

        self.frames_view.add_embedding_index(
            column=self.frames_view.im_caption,
            string_embed=clip.using(model_id="openai/clip-vit-base-patch32"),
        )

    def add_video(self, video_path: str):
        """
        Add a video to the pixel table.

        Args:
            video_path (str): The path to the video file.
        """
        if not self.video_table:
            raise ValueError(
                "Video table is not initialized. Call setup_table() first."
            )

        logger.info(f"Adding video {video_path} to table {self.video_table_name}")
        self.video_table.insert([{"video": video_path}])
