import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import pixeltable as pxt
from loguru import logger
from pixeltable.functions import openai
from pixeltable.functions.huggingface import clip
from pixeltable.functions.openai import embeddings, vision
from pixeltable.functions.video import extract_audio
from pixeltable.iterators import AudioSplitter
from pixeltable.iterators.video import FrameIterator

import kubrick_mcp.video.ingestion.registry as registry
from kubrick_mcp.config import get_settings
from kubrick_mcp.video.ingestion.functions import extract_text_from_chunk, resize_image
from kubrick_mcp.video.ingestion.tools import re_encode_video

if TYPE_CHECKING:
    from kubrick_mcp.video.ingestion.models import CachedTable

logger = logger.bind(name="VideoProcessor")
settings = get_settings()


class VideoProcessor:
    def __init__(
        self,
    ):
        self._pxt_cache: Optional[str] = None
        self._video_table = None
        self._frames_view = None
        self._audio_chunks = None
        self._video_mapping_idx: Optional[str] = None

        logger.info(
            "VideoProcessor initialized",
            f"\n Split FPS: {settings.SPLIT_FRAMES_COUNT}",
            f"\n Audio Chunk: {settings.AUDIO_CHUNK_LENGTH} seconds",
        )

    def setup_table(self, video_name: str):
        self._video_mapping_idx = video_name
        exists = self._check_if_exists(video_name)
        if exists:
            logger.info(f"Video index '{self._video_mapping_idx}' already exists and is ready for use.")
            cached_table: "CachedTable" = registry.get_table(self._video_mapping_idx)
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
                video_name=self._video_mapping_idx,
                video_cache=self.pxt_cache,
                frames_view_name=self.frames_view_name,
                audio_view_name=self.audio_view_name,
            )
            logger.info(f"Creating new video index '{self.video_table_name}' in '{self.pxt_cache}'")

    def _check_if_exists(self, video_path: str) -> bool:
        """
        Checks if the PixelTable table and related views/index for the video index exist.
        Returns:
            bool: True if current video index exists, False otherwise.
        """
        existing_tables = registry.get_registry()
        return video_path in existing_tables

    def _setup_table(self):
        self._setup_cache_directory()
        self._create_video_table()
        self._setup_audio_processing()
        self._setup_frame_processing()

    def _setup_cache_directory(self):
        logger.info(f"Creating cache path {self.pxt_cache}.")
        Path(self.pxt_cache).mkdir(parents=True, exist_ok=True)
        pxt.create_dir(self.pxt_cache, if_exists="replace_force")

    def _create_video_table(self):
        self.video_table = pxt.create_table(
            self.video_table_name,
            schema={"video": pxt.Video},
            if_exists="replace_force",
        )

    def _setup_audio_processing(self):
        self._add_audio_extraction()
        self._create_audio_chunks_view()
        self._add_audio_transcription()
        self._add_audio_text_extraction()
        self._add_audio_embedding_index()

    def _add_audio_extraction(self):
        self.video_table.add_computed_column(
            audio_extract=extract_audio(self.video_table.video, format="mp3"),
            if_exists="ignore",
        )

    def _create_audio_chunks_view(self):
        self.audio_chunks = pxt.create_view(
            self.audio_view_name,
            self.video_table,
            iterator=AudioSplitter.create(
                audio=self.video_table.audio_extract,
                chunk_duration_sec=settings.AUDIO_CHUNK_LENGTH,
                overlap_sec=settings.AUDIO_OVERLAP_SECONDS,
                min_chunk_duration_sec=settings.AUDIO_MIN_CHUNK_DURATION_SECONDS,
            ),
            if_exists="replace_force",
        )

    def _add_audio_transcription(self):
        self.audio_chunks.add_computed_column(
            transcription=openai.transcriptions(
                audio=self.audio_chunks.audio_chunk,
                model=settings.AUDIO_TRANSCRIPT_MODEL,
            ),
            if_exists="ignore",
        )

    def _add_audio_text_extraction(self):
        self.audio_chunks.add_computed_column(
            chunk_text=extract_text_from_chunk(self.audio_chunks.transcription),
            if_exists="ignore",
        )

    def _add_audio_embedding_index(self):
        self.audio_chunks.add_embedding_index(
            column=self.audio_chunks.chunk_text,
            string_embed=embeddings.using(model=settings.TRANSCRIPT_SIMILARITY_EMBD_MODEL),
            if_exists="ignore",
            idx_name="chunks_index",
        )

    def _setup_frame_processing(self):
        self._create_frames_view()
        self._add_frame_embedding_index()
        self._add_frame_captioning()
        self._add_caption_embedding_index()

    def _create_frames_view(self):
        self.frames_view = pxt.create_view(
            self.frames_view_name,
            self.video_table,
            iterator=FrameIterator.create(video=self.video_table.video, num_frames=settings.SPLIT_FRAMES_COUNT),
            if_exists="ignore",
        )
        self.frames_view.add_computed_column(
            resized_frame=resize_image(
                self.frames_view.frame,
                width=settings.IMAGE_RESIZE_WIDTH,
                height=settings.IMAGE_RESIZE_HEIGHT,
            )
        )

    def _add_frame_embedding_index(self):
        self.frames_view.add_embedding_index(
            column=self.frames_view.resized_frame,
            image_embed=clip.using(model_id=settings.IMAGE_SIMILARITY_EMBD_MODEL),
            if_exists="replace_force",
        )

    def _add_frame_captioning(self):
        self.frames_view.add_computed_column(
            im_caption=vision(
                prompt=settings.CAPTION_MODEL_PROMPT,
                image=self.frames_view.resized_frame,
                model=settings.IMAGE_CAPTION_MODEL,
            )
        )

    def _add_caption_embedding_index(self):
        self.frames_view.add_embedding_index(
            column=self.frames_view.im_caption,
            string_embed=embeddings.using(model=settings.CAPTION_SIMILARITY_EMBD_MODEL),
            if_exists="replace_force",
        )

    def add_video(self, video_path: str) -> bool:
        """
        Add a video to the pixel table.

        Args:
            video_path (str): The path to the video file.
        """
        if not self.video_table:
            raise ValueError("Video table is not initialized. Call setup_table() first.")
        logger.info(f"Adding video {video_path} to table {self.video_table_name}")

        new_video_path = re_encode_video(video_path=video_path)
        if new_video_path:
            self.video_table.insert([{"video": video_path}])
        return True
