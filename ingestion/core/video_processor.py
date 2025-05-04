import glob
import os
from pathlib import Path
from typing import List, Tuple
from uuid import uuid4

import pixeltable as pxt
import utils
from core.splitter import split_video_to_chunks_subprocess
from loguru import logger
from pixeltable.functions import whisper
from pixeltable.functions.huggingface import sentence_transformer
from pixeltable.functions.video import extract_audio
from pixeltable.iterators import AudioSplitter
from pixeltable.iterators.string import StringSplitter
from pixeltable.iterators.video import FrameIterator

logger = logger.bind(name="VideoProcessor")

DEFAULT_TMP_PATH = Path(os.getcwd()) / "/.cache/tmp"
VIDEO_INDEXES_REGISTRY = {}


class VideoProcessor:
    def __init__(self, pxt_cache: str = "poc", table_name: str = None, videos_cache: Path = DEFAULT_TMP_PATH):
        self.pxt_cache = pxt_cache
        self.videos_cache = videos_cache

        self.table_name = table_name if table_name else uuid4().hex

        self.full_table_name = f"{self.pxt_cache}.{self.table_name}"
        self.frames_view_name = f"{self.pxt_cache}.{self.table_name}_frames"
        self.audio_view_name = f"{self.pxt_cache}.{self.table_name}_audio_chunks"
        self.sentences_view_name = f"{self.pxt_cache}.{self.table_name}_sentences"
        self.semantics_index_name = f"{self.pxt_cache}.{self.table_name}_semanticindex"
        self.video_table = None

        if not self._check_if_exists():
            logger.info(f"Creating new video index '{self.table_name}' in '{self.pxt_cache}'")
            self._create_pxtable()
        else:
            logger.info(f"Video index '{self.full_table_name}' already exists and is ready for use.")

    def _check_if_exists(self) -> bool:
        """
        Checks if the Pyxet table and related views/index for the video index exist.

        Returns:
            bool: True if all components exist, False otherwise.
        """
        existing_tables = pxt.list_tables()
        if self.full_table_name in existing_tables:
            try:
                video_table = pxt.get_table(self.full_table_name)
                frames_view = pxt.get_table(self.frames_view_name)
                sentences_view = pxt.get_table(self.sentences_view_name)
                semantics_index = pxt.get_table(self.semantics_index_name)
                VIDEO_INDEXES_REGISTRY[self.full_table_name] = (
                    video_table,
                    frames_view,
                    sentences_view,
                    semantics_index,
                )
                return True
            except Exception as e:
                logger.warning(f"Error while accessing existing video index '{self.full_table_name}': {e}")
                return False
        return False

    def _create_pxtable(self):
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

    def preprocess_video(self, video_path, chunk_duration: int) -> Tuple[str, List[str]]:
        vpath = Path(video_path)
        assert vpath.exists(), f"Video could not be found {video_path}"

        if Path(self.videos_cache).exists():
            clips_cache = self.videos_cache
        clips_cache = split_video_to_chunks_subprocess(
            video_path=vpath, chunk_duration=chunk_duration, cache_path=self.videos_cache
        )
        video_files = glob.glob(str(clips_cache) + "/*.mp4")
        video_files.sort()

        return clips_cache, video_files

    def add_video(self, video_path: str):
        self.video_table.insert([{"video": video_path, "uploaded_at": pxt.now()}])

    def get_video_clip(self, user_query: str, top_k: int) -> Path:
        sims = self.sentences_view.text.similarity(user_query)
        results_df = (
            self.sentences_view.select(
                self.sentences_view.pos,
                self.sentences_view.start_time_sec,
                self.sentences_view.end_time_sec,
                similarity=sims,
            )
            .order_by(sims, asc=False)
            .limit(top_k)
            .collect()
            .to_pandas()
        )

        best_entry_index = results_df["similarity"].idxmax()
        best_start_time = results_df.loc[best_entry_index, "start_time_sec"]
        best_end_time = results_df.loc[best_entry_index, "end_time_sec"]

        frames = (
            self.frames_view.select(
                self.frames_view.frame,
            )
            .where(
                (self.frames_view.pos_msec >= best_start_time * 1e3)
                & (self.frames_view.pos_msec <= best_end_time * 1e3)
            )
            .order_by(self.frames_view.frame_idx)
        )

        video_path = utils.create_video_from_dataframe(
            frames, self.videos_cache / f"{self.table_name}_{uuid4().hex}.mp4"
        )

        return video_path
