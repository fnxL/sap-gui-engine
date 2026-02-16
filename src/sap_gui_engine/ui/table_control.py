import logging
from typing import TYPE_CHECKING, Any, Optional

from ..constants import GuiObject, VKey
from ..exceptions import SAPTableConfigurationError
from .vcomponent import GuiVComponent

if TYPE_CHECKING:
    from ..core import SAPGuiEngine

logger = logging.getLogger(__name__)


class GuiTableControl:
    def __init__(
        self,
        element: Any,
        table_id: str,
        __parent_class__: "SAPGuiEngine",
    ):
        if element.type != GuiObject.TABLE_CONTROL:
            raise ValueError(f"Element {element.name} is not a GuiTableControl")

        self.id = table_id
        self._element = element
        self._parent_class = __parent_class__

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the underlying SAP element."""
        return getattr(self._element, name)

    def __setattr__(self, name, value):
        """Delegate attribute setting to underlying sap element, but handle internal attributes normally."""
        try:
            element = object.__getattribute__(self, "_element")
            if hasattr(element, name):
                setattr(element, name, value)
        except AttributeError:
            # Fallback
            pass

        object.__setattr__(self, name, value)

    def fill(
        self,
        data: list[dict[str, Any]],
        columns: list[str] | None = None,
        exclude_columns: list[str] | None = None,
        set_focus: bool = False,
    ):
        if columns and exclude_columns:
            raise ValueError("Cannot specify both 'columns' and 'exclude_columns'.")

        if not data:
            raise ValueError("Provided Data is Empty.")

        self.column_map = self._get_column_map(columns, exclude_columns)
        self.visible_rows = self.VisibleRowCount

        # Check if table is empty (scroll max == 0 usually implies empty or single page)
        is_table_empty = self.VerticalScrollbar.Maximum == 0
        logger.info(
            f"Filling table {self.id} ({len(data)} rows). Mode: {'Fill empty' if is_table_empty else 'Overwrite'}"
        )
        # Reset scroll position for overwriting existing data
        if not is_table_empty:
            self.VerticalScrollbar.Position = 0
            self._refresh_table()

        # Choose pagination strategy based on table state
        pagination_key = VKey.ENTER if is_table_empty else VKey.PAGE_DOWN
        next_row_idx_after_pagination = 1 if is_table_empty else 0

        self._fill_table(
            data=data,
            pagination_key=pagination_key,
            next_row_idx_after_pagination=next_row_idx_after_pagination,
            set_focus=set_focus,
        )

    def _fill_table(
        self,
        data: list[dict[str, Any]],
        pagination_key: VKey,
        next_row_idx_after_pagination: int,
        set_focus: bool = False,
    ):
        """Internal method to fill table data with the given pagination strategy."""
        page = 1
        current_row_idx = 0
        # Note: I chose to iterate over colum_map, because length of column_map might be lesser than the length of row

        for row in data:
            # Update all cells for the current row
            self._upate_row_cells(
                row_idx=current_row_idx, row=row, page=page, set_focus=set_focus
            )

            # SAP quirk: Pagination logic after reaching the last visible row

            # For empty tables (ENTER): Saves current page and shows new empty rows. Often the last row of prev page becomes first row of next page. So after the first page, we need to start from row index 1

            # For existing tables (PAGE_DOWN): Scrolls to next page of existing data. PageDown usually scrolls a full page, so start at 0.
            if current_row_idx == self.visible_rows - 1:
                logger.debug("Moving to next page")
                self._paginate_table(pagination_key)
                self._refresh_table()
                page += 1
                current_row_idx = next_row_idx_after_pagination
            else:
                current_row_idx += 1

        # Final commit
        self._parent_class.press_enter()
        self._parent_class.dismiss_popups()
        self._parent_class.raise_if_error_dialog(
            exception=SAPTableConfigurationError,
            message="Error while filling table:",
        )

    def _upate_row_cells(
        self,
        row_idx: int,
        row: dict[str, Any],
        page: int,
        set_focus: bool = False,
    ):
        # Note: I chose to iterate over colum_map, because length of column_map might be lesser than the length of row
        for col, col_idx in self.column_map.items():
            if col in row and row.get(col) is not None:
                logger.debug(
                    f"Updating {col} of row {row_idx} to value: {row[col]} | col_idx: {col_idx} | Page: {page}"
                )
                self._update_cell(
                    row_idx=row_idx,
                    col_idx=col_idx,
                    value=row[col],
                    col_name=col,
                    set_focus=set_focus,
                )

    def _update_cell(
        self,
        row_idx: int,
        col_idx: int,
        value: Any,
        col_name: str,
        set_focus: bool = False,
    ) -> None:
        cell = self.GetCell(row_idx, col_idx)
        if set_focus:
            cell.setFocus()

        # Check if the cell is a combobox and convert it to a GuiComponent type to support setting the combobox values by .text property
        if cell.type == GuiObject.COMBO_BOX:
            cell = GuiVComponent(cell)

        # only update if the cell is changeable
        if cell.changeable:
            cell.text = str(value).strip()
            return

        logger.warning(
            f"Cell of column '{col_name}' at {row_idx}, {col_idx} is not changeable"
        )
        return

    def _paginate_table(
        self,
        pagination_key: VKey,
    ):
        self._parent_class.send_vkey(pagination_key)
        self._parent_class.dismiss_popups()
        self._parent_class.raise_if_error_dialog(
            exception=SAPTableConfigurationError,
            message="Error while filling table:",
        )

    def _refresh_table(self):
        """
        Refreshes the underlying table element reference
        """
        self._element = self._parent_class.find_by_id(self.id)

    def _get_column_map(
        self,
        include_cols: Optional[list[str]] = None,
        exclude_cols: Optional[list[str]] = None,
    ) -> dict[str, int]:
        """
        Creates a mapping of column titles (lowercase) to column indices.

        Args:
            include_cols: List of column titles to include.
            exclude_cols: List of column titles to exclude.

        Returns:
            Dict[str, int]: Map of 'column title' -> index.
        """
        if include_cols and exclude_cols:
            raise ValueError("Cannot specify both include_cols and exclude_cols")

        full_map = {}
        for i, col in enumerate(self.columns):
            title = str(getattr(col, "title", "") or "").strip().lower()
            if title:
                full_map[title] = i

        if include_cols:
            whitelist = {c.lower() for c in include_cols}
            return {title: idx for title, idx in full_map.items() if title in whitelist}

        if exclude_cols:
            blacklist = {c.lower() for c in exclude_cols}
            return {
                title: idx for title, idx in full_map.items() if title not in blacklist
            }

        return full_map
