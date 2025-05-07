from typing import Dict
from uuid import uuid4

import pixeltable as pxt
from core.models import CachedTable, CachedTableMetadata
from loguru import logger
from pixeltable.functions import whisper
from pixeltable.functions.huggingface import sentence_transformer
from pixeltable.functions.video import extract_audio
from pixeltable.iterators import AudioSplitter
from pixeltable.iterators.string import StringSplitter
from pixeltable.iterators.video import FrameIterator

logger = logger.bind(name="VideoProcessor")

VIDEO_INDEXES_REGISTRY: Dict[str, CachedTableMetadata] = {}


def get_registry() -> Dict[str, CachedTableMetadata]:
    """
    Get the global video index registry.

    Returns:
        Dict[str, CachedTableMetadata]: The video index registry.
    """
    return VIDEO_INDEXES_REGISTRY


def add_index_to_registry(
    video_name: str,
    video_cache: str,
    video_table_name: str,
    frames_view_name: str,
    sentences_view_name: str,
    semantics_index_name: str,
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
    VIDEO_INDEXES_REGISTRY[video_name] = {
        video_name: CachedTableMetadata(
            video_cache=video_cache,
            video_table=video_table_name,
            frames_view=frames_view_name,
            sentences_view=sentences_view_name,
            semantics_index=semantics_index_name,
        )
    }


def get_table(video_name: str) -> Dict[str, CachedTable]:
    """
    Get the global video index registry.

    Returns:
        Dict[str, CachedTable]: The video index registry.
    """
    metadata = VIDEO_INDEXES_REGISTRY.get(video_name)
    return CachedTable().from_metadata(metadata)


class VideoProcessor:
    def __init__(self, video_clip_length: int = 60, split_fps: float = 1.0, audio_chunk_length: float = 30):
        self.clip_len = video_clip_length
        self.split_fps = split_fps
        self.audio_chunk_length = audio_chunk_length

        logger.info(
            f"VideoProcessor initialized with clip length: {self.clip_len}, split fps: {self.split_fps}, audio chunk length: {self.audio_chunk_length}"
        )

    def setup_table(self, cache: str, table_name: str):
        self.pxt_cache = cache

        self.table_name = table_name if table_name else uuid4().hex

        self.full_table_name = f"{self.pxt_cache}.{self.table_name}"
        self.frames_view_name = f"{self.pxt_cache}.{self.table_name}_frames"
        self.audio_view_name = f"{self.pxt_cache}.{self.table_name}_audio_chunks"
        self.sentences_view_name = f"{self.pxt_cache}.{self.table_name}_sentences"
        self.semantics_index_name = f"{self.pxt_cache}.{self.table_name}_semanticindex"
        self.video_table = None

        if not self._check_if_exists():
            logger.info(f"Creating new video index '{self.table_name}' in '{self.pxt_cache}'")
            self._create_table()
        else:
            logger.info(f"Video index '{self.full_table_name}' already exists and is ready for use.")

    def _check_if_exists(self) -> bool:
        """
        Checks if the Pyxet table and related views/index for the video index exist.

        Returns:
            bool: True if all components exist, False otherwise.
        """
        existing_tables = pxt.list_tables()
        if self.full_table_name not in existing_tables:
            try:
                add_index_to_registry(
                    video_name=self.table_name,
                    video_cache=self.pxt_cache,
                    video_table_name=self.full_table_name,
                    frames_view_name=self.frames_view_name,
                    sentences_view_name=self.sentences_view_name,
                    semantics_index_name=self.semantics_index_name,
                )
                return False
            except Exception as e:
                logger.warning(f"Error while accessing existing video index '{self.full_table_name}': {e}")
                return False
        return True

    def _create_table(self):
        pxt.drop_dir(self.pxt_cache, force=True)
        pxt.create_dir(self.pxt_cache, if_exists="ignore")

        self.video_table = pxt.create_table(
            self.full_table_name,
            {"video": pxt.Video},
            if_exists="ignore",
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

        # STEP 2: transcribe audio channel
        self.audio_chunks.add_computed_column(
            transcription=whisper.transcribe(audio=self.audio_chunks.audio, model="base.en"),
            if_exists="ignore",
        )

        self.frames_view = pxt.create_view(
            self.frames_view_name,
            self.video_table,
            iterator=FrameIterator.create(video=self.video_table.video, fps=1.0),  # FIXME: move to config
            if_exists="ignore",
        )

        # Step 4: caption an entire video
        # DEPCRECATED: Will caption frames instead
        # self.video_table.add_computed_column(
        #     video_caption=caption_video(video=self.video_table.video, prompt="Describe the video in detail."),
        # )

        # self.video_table.add_computed_column(
        #     semantics=compose_semantics(self.video_table.video_caption, self.video_table.transcription),
        #     if_exists="replace",
        # )

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
        )

    def add_video(self, video_path: str):
        """
        Add a video to the pixel table.

        Args:
            video_path (str): The path to the video file.
        """
        if not self.video_table:
            raise ValueError("Video table is not initialized. Call setup_table() first.")

        logger.info(f"Adding video {video_path} to table {self.full_table_name}")
        self.video_table.insert([{"video": video_path}])
