import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict

import pixeltable as pxt
from core.functions import caption_video, extract_text_from_chunk
from core.models import CachedTable, CachedTableMetadata
from loguru import logger
from pixeltable.functions import whisper
from pixeltable.functions.huggingface import sentence_transformer
from pixeltable.functions.video import extract_audio
from pixeltable.iterators import AudioSplitter
from pixeltable.iterators.string import StringSplitter
from pixeltable.iterators.video import FrameIterator

logger = logger.bind(name="VideoProcessor")

DEFAULT_INDEX_DIR = ".records"
VIDEO_INDEXES_REGISTRY: Dict[str, CachedTableMetadata] = {}


def get_registry() -> Dict[str, CachedTableMetadata]:
    """
    Get the global video index registry.

    Returns:
        Dict[str, CachedTableMetadata]: The video index registry.
    """
    global VIDEO_INDEXES_REGISTRY
    if not VIDEO_INDEXES_REGISTRY:
        try:
            registry_files = [
                f for f in os.listdir(DEFAULT_INDEX_DIR) if f.startswith("registry_") and f.endswith(".json")
            ]
            if registry_files:
                latest_registry = Path(DEFAULT_INDEX_DIR) / max(registry_files)
                with open(str(latest_registry), "r") as f:
                    VIDEO_INDEXES_REGISTRY = json.load(f)
                    for key, value in VIDEO_INDEXES_REGISTRY.items():
                        VIDEO_INDEXES_REGISTRY[key] = CachedTableMetadata(**value)
                logger.info(f"Loading registry from {latest_registry}")
        except FileNotFoundError:
            logger.warning("Registry file not found. Returning empty registry.")
    else:
        logger.info("Using existing video index registry.")
    return VIDEO_INDEXES_REGISTRY


def add_index_to_registry(
    video_name: str,
    video_cache: str,
    frames_view_name: str,
    sentences_view_name: str,
    audio_view_name: str,
):
    """
    Register a video index in the global registry.

    Args:
        video_path (str): The path to the video file.
        video_name (str): The name of the video.
        video_cache (str): The cache path for the video.
        video_table_name (str): The name of the video table.
        frames_view_name (str): The name of the frames view.
        sentences_view_name (str): The name of the sentences view.
        semantics_index_name (str): The name of the semantics index.

    """
    global VIDEO_INDEXES_REGISTRY
    VIDEO_INDEXES_REGISTRY[video_name] = CachedTableMetadata(
        video_cache=video_cache,
        video_table=video_cache,
        frames_view=frames_view_name,
        sentences_view=sentences_view_name,
        audio_chunks_view=audio_view_name,
    )
    dt = datetime.datetime.now()
    dtstr = dt.strftime("%Y-%m-%d%H:%M:%S")
    records_dir = Path(DEFAULT_INDEX_DIR)
    records_dir.mkdir(parents=True, exist_ok=True)
    with open(records_dir / f"registry_{dtstr}.json", "w") as f:
        json.dump(VIDEO_INDEXES_REGISTRY, f, indent=4)

    logger.info(f"Video index '{video_name}' registered in the global registry.")


def get_table(video_name: str) -> Dict[str, CachedTable]:
    """
    Get the global video index registry.

    Returns:
        Dict[str, CachedTable]: The video index registry.
    """
    registry = get_registry()
    metadata = registry.get(video_name)
    return CachedTable.from_metadata(metadata)


class VideoProcessor:
    def __init__(self, video_clip_length: int = 60, split_fps: float = 1.0, audio_chunk_length: float = 30):
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
            logger.info(f"Video index '{self.video_mapping_idx}' already exists and is ready for use.")
            cached_table: CachedTable = get_table(self.video_mapping_idx)
            self.pxt_cache = cached_table.video_cache
            self.video_table = cached_table.video_table
            self.frames_view = cached_table.frames_view
            self.audio_chunks = cached_table.audio_chunks_view
            self.sentences_view = cached_table.sentences_view

        else:
            self.pxt_cache = f"cache_{uuid.uuid4().hex[-4:]}"
            self.video_table_name = f"{self.pxt_cache}.table"
            self.frames_view_name = f"{self.video_table_name}_frames"
            self.audio_view_name = f"{self.video_table_name}_audio_chunks"
            self.sentences_view_name = f"{self.video_table_name}_sentences"
            self.video_table = None

            self._create_table()

            add_index_to_registry(
                video_name=self.video_mapping_idx,
                video_cache=self.pxt_cache,
                video_table_name=self.video_table_name,
                frames_view_name=self.frames_view_name,
                sentences_view_name=self.sentences_view_name,
                audio_view_name=self.audio_view_name,
            )
            logger.info(f"Creating new video index '{self.video_table_name}' in '{self.pxt_cache}'")

    def _check_if_exists(self) -> bool:
        """
        Checks if the PixelTable table and related views/index for the video index exist.

        Returns:
            bool: True if all components exist, False otherwise.
        """
        existing_tables = get_registry()
        return self.video_mapping_idx in existing_tables

    def _create_table(self):
        logger.info(f"Creating cache path {self.pxt_cache}.")
        Path(self.pxt_cache).mkdir(parents=True, exist_ok=True)
        pxt.create_dir(self.pxt_cache, if_exists="ignore")

        self.video_table = pxt.create_table(
            self.video_table_name,
            schema={"video": pxt.Video, "video_index": pxt.type_system.Int},
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
                chunk_duration_sec=30.0,
                overlap_sec=1.0,
                min_chunk_duration_sec=5.0,
            ),
            if_exists="ignore",
        )

        self.audio_chunks.add_computed_column(
            transcription=whisper.transcribe(audio=self.audio_chunks.audio_chunk, model="base.en"),
            if_exists="ignore",
        )
        self.audio_chunks.add_computed_column(
            chunk_text=extract_text_from_chunk(self.audio_chunks.transcription),
            if_exists="ignore",
        )

        self.frames_view = pxt.create_view(
            self.frames_view_name,
            self.video_table,
            iterator=FrameIterator.create(video=self.video_table.video, fps=1.0),  # FIXME: move to config
            if_exists="ignore",
        )

        self.video_table.add_computed_column(
            video_caption=caption_video(
                video=self.video_table.video,
                prompt="Describe the video in detail. Do not hallucinate.Keep it short.",  # FIXME: move to config
            ),
            if_exists="ignore",
        )

        self.sentences_view = pxt.create_view(
            self.sentences_view_name,
            self.audio_chunks,
            iterator=StringSplitter.create(text=self.audio_chunks.transcription.text, separators="sentence"),
            if_exists="ignore",
        )

        # Step 7: Add the embedding index for the sentences
        self.sentences_view.add_embedding_index(
            column=self.sentences_view.text,  # this comes from L80, as iterator creates `text` rows`
            string_embed=sentence_transformer.using(model_id="intfloat/e5-large-v2"),
            if_exists="ignore",
            idx_name="sentences_index",
        )

        self.audio_chunks.add_embedding_index(
            column=self.audio_chunks.chunk_text,
            string_embed=sentence_transformer.using(model_id="intfloat/e5-large-v2"),
            if_exists="ignore",
            idx_name="chunks_index",
        )

    def add_video(self, video_path: str, video_index: int = 0):
        """
        Add a video to the pixel table.

        Args:
            video_path (str): The path to the video file.
        """
        if not self.video_table:
            raise ValueError("Video table is not initialized. Call setup_table() first.")

        logger.info(f"Adding video {video_path} to table {self.video_table_name}")
        self.video_table.insert([{"video": video_path, "video_index": video_index}])
