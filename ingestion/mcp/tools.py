import os

import pixeltable as pxt

pixel_table_cache = os.getenv("PIXELTABLE_CACHE", "poc")


def list_tables() -> str:
    """List all video indexes currently available.

    Returns:
        A string listing the current video indexes.
    """
    tables = pxt.list_tables()
    video_tables = [t for t in tables if t.startswith(f"{DIRECTORY}.")]
    return f"Current video indexes: {', '.join(video_tables)}" if video_tables else "No video indexes exist."
