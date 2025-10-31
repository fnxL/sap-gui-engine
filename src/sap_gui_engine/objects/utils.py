def get_column_idx_map(
    table, columns: list[str] | None = None, exclude_columns: list[str] | None = None
):
    """
    Gets a mapping of lowercase SAP table column titles to their index.

    Args:
        columns (optional): If provided, returns only columns specified in this list.
        exclude_columns (optional): If provided, returns all columns except those in this list.

    Returns:
        A dictionary mapping column titles to their zero-based index.

    Raises:
        ValueError: If both columns  and exclude_columns are provided.
    """
    if columns and exclude_columns:
        raise ValueError(
            "Both filter_columns and exclude_columns cannot be used together"
        )

    full_col_idx_map = {}
    for i, col in enumerate(table.columns):
        title = (getattr(col, "title", None) or "").strip().lower()
        if title:
            full_col_idx_map[title] = i

    if columns:
        filter_set = {col.lower() for col in columns}
        return {
            title: idx for title, idx in full_col_idx_map.items() if title in filter_set
        }

    if exclude_columns:
        exclude_set = {col.lower() for col in exclude_columns}
        return {
            title: idx
            for title, idx in full_col_idx_map.items()
            if title not in exclude_set
        }

    return full_col_idx_map
