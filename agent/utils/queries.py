import pixeltable as pxt


@pxt.query
def get_recent_memory(current_timestamp: pxt.Timestamp, memory_table: pxt.Table, history_len: int) -> list[dict]:
    """
    Get recent messages from memory, respecting n_latest_messages limit if set.
    Messages are ordered by timestamp (newest first).
    """
    query = (
        memory_table.where(memory_table.timestamp < current_timestamp)
        .order_by(memory_table.timestamp, asc=False)
        .select(role=memory_table.role, content=memory_table.content)
    )
    if history_len is not None:
        query = query.limit(history_len)
    return query
