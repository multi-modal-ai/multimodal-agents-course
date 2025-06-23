import json
import os
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Dict

from loguru import logger

import kubrick_mcp.video.ingestion.constants as cc
from kubrick_mcp.video.ingestion.models import CachedTable, CachedTableMetadata

logger = logger.bind(name="TableRegistry")


VIDEO_INDEXES_REGISTRY: Dict[str, CachedTableMetadata] = {}


# Hit cache on multiple calls to get_registry
@lru_cache(maxsize=1)
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
                f
                for f in os.listdir(cc.DEFAULT_CACHED_TABLES_REGISTRY_DIR)
                if f.startswith("registry_") and f.endswith(".json")
            ]
            if registry_files:
                latest_file = max(registry_files)
                latest_registry = (
                    Path(cc.DEFAULT_CACHED_TABLES_REGISTRY_DIR) / latest_file
                )
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
        video_table=f"{video_cache}.table",  # FIXME: this is a hack, should be fixed before passed here
        frames_view=frames_view_name,
        audio_chunks_view=audio_view_name,
    ).model_dump()
    dt = datetime.now()
    dtstr = dt.strftime("%Y-%m-%d%H:%M:%S")
    records_dir = Path(cc.DEFAULT_CACHED_TABLES_REGISTRY_DIR)
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
    logger.info(f"Registry: {registry}")
    metadata = registry.get(video_name)
    logger.info(f"Metadata: {metadata}")
    return CachedTable.from_metadata(metadata)
