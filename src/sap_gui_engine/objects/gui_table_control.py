from typing import Any
from .gui_component import GuiComponent

class GuiTableControl:
    def __init__(self, element: Any):
        self.element = element
        self.type = element.type
        self.columns = element.columns
        self.rowCount = element.rowCount
        self.visibleRowCount = element.VisibleRowCount
        self.rows = element.rows

    @property
    def vertical_scroll_position(self):
        return self.element.VerticalScrollbar.Position

    @vertical_scroll_position.setter
    def vertical_scroll_position(self, position: int):
        try:
            self.element.VerticalScrollbar.Position = position
        except Exception as e:
            raise RuntimeError(f"Error setting vertical scroll position: {str(e)}")

    def get_cell(self, row: int, column: int):
        cell = self.element.GetCell(row, column)

        if cell.type == "GuiComboBox":
            return GuiComponent(cell)

        return cell

    def get_column_idx_map(
        self, columns: list[str] | None = None, exclude_columns: list[str] | None = None
    ):
        """
        Gets a mapping of lowercase SAP table column titles to their index. This method is only applicable to GuiTableControl.

        Args:
            columns (optional): If provided, returns only columns specified in this list.
            exclude_columns (optional): If provided, returns all columns except those in this list.

        Returns:
            A dictionary mapping column titles to their zero-based index.

        Raises:
            ValueError: If both columns  and exclude_columns are provided.
        """

        if self.type != "GuiTableControl":
            raise ValueError(f"Element {self.element.name} is not a table")

        if columns and exclude_columns:
            raise ValueError(
                "Both filter_columns and exclude_columns cannot be used together"
            )

        full_col_idx_map = {}

        for i, col in enumerate(self.columns):
            title = (getattr(col, "title", None) or "").strip().lower()
            if title:
                full_col_idx_map[title] = i

        if columns:
            filter_set = {col.lower() for col in columns}
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
