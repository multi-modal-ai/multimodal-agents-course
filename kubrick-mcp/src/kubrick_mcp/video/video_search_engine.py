from typing import Any, Dict, List

import kubrick_mcp.video.ingestion.registry as registry
from kubrick_mcp.config import get_settings
from kubrick_mcp.video.ingestion.models import CachedTable
from kubrick_mcp.video.ingestion.tools import decode_image

settings = get_settings()


class VideoSearchEngine:
    """A class that provides video search capabilities using different modalities."""

    def __init__(self, video_name: str):
        """Initialize the video search engine.

        Args:
            video_name (str): The name of the video index to search in.

        Raises:
            ValueError: If the video index is not found in registry.
        """
        self.video_index: CachedTable = registry.get_table(video_name)
        if not self.video_index:
            raise ValueError(f"Video index {video_name} not found in registry.")
        self.video_name = video_name

    def search_by_speech(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Search video clips by speech similarity.

        Args:
            query (str): The search query to match against speech content.
            top_k (int, optional): Number of top results to return. Defaults to settings.SPEECH_SIMILARITY_SEARCH_TOP_K.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing clip information with keys:
                - start_time (float): Start time in seconds
                - end_time (float): End time in seconds
                - similarity (float): Similarity score
        """
        sims = self.video_index.audio_chunks_view.chunk_text.similarity(query)
        results = self.video_index.audio_chunks_view.select(
            self.video_index.audio_chunks_view.pos,
            self.video_index.audio_chunks_view.start_time_sec,
            self.video_index.audio_chunks_view.end_time_sec,
            similarity=sims,
        ).order_by(sims, asc=False)

        return [
            {
                "start_time": float(entry["start_time_sec"]),
                "end_time": float(entry["end_time_sec"]),
                "similarity": float(entry["similarity"]),
            }
            for entry in results.limit(top_k).collect()
        ]

    def search_by_image(self, image_base64: str, top_k: int) -> List[Dict[str, Any]]:
        """Search video clips by image similarity.

        Args:
            image_base64 (str): The query image to match against video frames.
            top_k (int, optional): Number of top results to return. Defaults to settings.IMAGE_SIMILARITY_SEARCH_TOP_K.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing clip information with keys:
                - start_time (float): Start time in seconds
                - end_time (float): End time in seconds
                - similarity (float): Similarity score
        """
        image = decode_image(image_base64)
        sims = self.video_index.frames_view.resized_frame.similarity(image)
        results = self.video_index.frames_view.select(
            self.video_index.frames_view.pos_msec,
            self.video_index.frames_view.resized_frame,
            similarity=sims,
        ).order_by(sims, asc=False)

        return [
            {
                "start_time": entry["pos_msec"] / 1000.0 - settings.DELTA_SECONDS_FRAME_INTERVAL,
                "end_time": entry["pos_msec"] / 1000.0 + settings.DELTA_SECONDS_FRAME_INTERVAL,
                "similarity": float(entry["similarity"]),
            }
            for entry in results.limit(top_k).collect()
        ]

    def search_by_caption(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Search video clips by caption similarity.

        Args:
            query (str): The search query to match against frame captions.
            top_k (int, optional): Number of top results to return. Defaults to settings.CAPTION_SIMILARITY_SEARCH_TOP_K.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing clip information with keys:
                - start_time (float): Start time in seconds
                - end_time (float): End time in seconds
                - similarity (float): Similarity score
        """
        sims = self.video_index.frames_view.im_caption.similarity(query)
        results = self.video_index.frames_view.select(
            self.video_index.frames_view.pos_msec,
            self.video_index.frames_view.im_caption,
            similarity=sims,
        ).order_by(sims, asc=False)

        return [
            {
                "start_time": entry["pos_msec"] / 1000.0 - settings.DELTA_SECONDS_FRAME_INTERVAL,
                "end_time": entry["pos_msec"] / 1000.0 + settings.DELTA_SECONDS_FRAME_INTERVAL,
                "similarity": float(entry["similarity"]),
            }
            for entry in results.limit(top_k).collect()
        ]

    def get_speech_info(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Get speech text information based on query similarity.

        Args:
            query (str): The search query to match against speech content.
            top_k (int, optional): Number of top results to return. Defaults to settings.SPEECH_SIMILARITY_SEARCH_TOP_K.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing text information with keys:
                - text (str): The speech text
                - similarity (float): Similarity score
        """
        sims = self.video_index.audio_chunks_view.chunk_text.similarity(query)
        results = self.video_index.audio_chunks_view.select(
            self.video_index.audio_chunks_view.chunk_text,
            similarity=sims,
        ).order_by(sims, asc=False)

        return [
            {
                "text": entry["chunk_text"],
                "similarity": float(entry["similarity"]),
            }
            for entry in results.limit(top_k).collect()
        ]

    def get_caption_info(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Get caption information based on query similarity.

        Args:
            query (str): The search query to match against frame captions.
            top_k (int, optional): Number of top results to return. Defaults to settings.CAPTION_SIMILARITY_SEARCH_TOP_K.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing caption information with keys:
                - caption (str): The frame caption
                - similarity (float): Similarity score
        """
        sims = self.video_index.frames_view.im_caption.similarity(query)
        results = self.video_index.frames_view.select(
            self.video_index.frames_view.im_caption,
            similarity=sims,
        ).order_by(sims, asc=False)

        return [
            {
                "caption": entry["im_caption"],
                "similarity": float(entry["similarity"]),
            }
            for entry in results.limit(top_k).collect()
        ]
