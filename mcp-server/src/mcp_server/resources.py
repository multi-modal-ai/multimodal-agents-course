from mcp_server.video.ingestion.models import CachedTable, CachedTableMetadata
from mcp_server.video.ingestion.registry import get_registry


def list_tables() -> str:
    """List all video indexes currently available.

    Returns:
        A string listing the current video indexes.
    """
    keys = list(get_registry().keys())
    if not keys:
        return "No video indexes exist."
    return f"Current video indexes: {', '.join(keys)}"


def list_table_info(table_name: str) -> str:
    """List information about a specific video index.

    Args:
        table_name: The name of the video index to list information for.

    Returns:
        A string with the information about the video index.
    """
    registry = get_registry()
    if table_name not in registry:
        return f"Video index '{table_name}' does not exist."
    table_metadata = registry[table_name]
    table_info = CachedTableMetadata(**table_metadata)
    table = CachedTable.from_metadata(table_info)
    return f"Video index '{table_name}' info: {' | '.join(table.video_table.columns)}"
