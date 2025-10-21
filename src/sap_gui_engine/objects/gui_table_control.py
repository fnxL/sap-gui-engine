import logging
from .gui_component import GuiComponent
from typing import Any

logger = logging.getLogger(__name__)


class GuiTableControl(GuiComponent):
    def __init__(self, element: Any):
        super().__init__(element)
        self.columns = self.element.Columns
        self.visible_row_count = self.element.VisibleRowCount  # Number of visible rows in the table. This is fixed based on your font size/resolution.
        self.row_count = (
            self.element.Rows
        )  # Number of rows in the table, includes invisible rows.

    def get_column_idx_map(
        self,
        filter_columns: list[str] | None = None,
        exclude_columns: list[str] | None = None,
    ) -> dict[str, int]:
        """
        Gets a mapping of lowercase column titles to their index.

        Args:
            filter_columns (optional): If provided, returns only columns in this list.
            exclude_columns (optional): If provided, returns all columns except those in this list.

        Returns:
            A dictionary mapping column titles to their zero-based index.

        Raises:
            ValueError: If both filter_columns and exclude_columns are provided.
        """

        if filter_columns and exclude_columns:
            raise ValueError(
                "Both filter_columns and exclude_columns cannot be used together"
            )

        full_col_idx_map = {}
        for i, col in enumerate(self.columns):
            title = (getattr(col, "title", None) or "").strip().lower()
            if title:
                full_col_idx_map[title] = i

        if filter_columns:
            filter_set = {col.lower() for col in filter_columns}
            return {
                title: idx
                for title, idx in full_col_idx_map.items()
                if title in filter_set
            }

        if exclude_columns:
            exclude_set = {col.lower() for col in exclude_columns}
            return {
                title: idx
                for title, idx in full_col_idx_map.items()
                if title not in exclude_set
            }

        return full_col_idx_map

    def set_scroll_position(self, position: int):
        try:
            self.element.verticalScrollbar.position = position
        except Exception as e:
            logger.error(f"Error setting scroll position: {e}")
            raise RuntimeError(f"Error setting scroll position: {e}") from e
        return True

    def get_cell(self, row: int, col: int):
        """
        Returns:
            The given table cell. This method is more efficient than accessing a single cell by findById.
        Args:
            row: Zero-based index of row
            col: Zero-based index of column.
        """
        return self.element.GetCell(row, col)
