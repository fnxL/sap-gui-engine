import logging
from typing import TYPE_CHECKING, Any

from sap_gui_engine.constants import GuiObject, VKey
from sap_gui_engine.exceptions import (
    SAPElementNotChangeable,
    SAPTableConfigurationError,
)

from .gui_vcomponent import GuiVComponent

if TYPE_CHECKING:
    from .gui_session import GuiSession

logger = logging.getLogger(__name__)


class GuiTableControl:
    def __init__(
        self,
        com_element: Any,
        table_id: str,
        __parent_class__: "GuiSession",
    ):
        if com_element.type != GuiObject.TABLE_CONTROL:
            raise SAPElementNotChangeable(
                f"Element {com_element.name} is not a GuiTableControl. It is a {com_element.type} type"
            )

        self.id = table_id
        self._com_element = com_element
        self.__parent_class__ = __parent_class__

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the underlying SAP element."""
        return getattr(self._com_element, name)

    def __setattr__(self, name, value):
        """
        Set attributes on the GuiTableControl instance or delegate to the underlying _com_element if the attribute doesn't exist on the instance itself.
        """
        try:
            element = object.__getattribute__(self, "_element")
            if hasattr(element, name):
                setattr(element, name, value)
        except AttributeError:
            # Fallback
            pass
        object.__setattr__(self, name, value)

    @property
    def visible_rows(self) -> int:
        return self._com_element.VisibleRowCount

    def get_table_headers(
        self,
        headers: list[str] | None = None,
        exclude_headers: list[str] | None = None,
        lowercase: bool = True,
    ) -> dict[str, int]:
        """
        Creates a mapping of table headers (lowercase by default) to header index

        Parameters
        ----------
        headers : list[str] | None
            List of headers to include. If None, all headers of the table are included, by default None.
        exclude_headers : list[str] | None
            List of headers to exclude. If None, no headers are excluded, by default None.
        lowercase : bool, optional
            Whether to return the lowercase headers, by default True

        Returns
        -------
        dict[str, int]
            Mapping of header name to header index.
        """
        if headers and exclude_headers:
            raise ValueError("Cannot specify both headers and exclude_headers")

        full_map = {}
        for i, col in enumerate(self._com_element.Columns):
            title = str(getattr(col, "title", "") or "").strip()
            if lowercase:
                title = title.lower()

            if title:
                full_map[title] = i

        if headers:
            whitelist = {c.lower() for c in headers}
            return {
                title: idx
                for title, idx in full_map.items()
                if title.lower() in whitelist
            }

        if exclude_headers:
            blacklist = {c.lower() for c in exclude_headers}
            return {
                title: idx
                for title, idx in full_map.items()
                if title.lower() not in blacklist
            }

        return full_map

    def fill(
        self,
        data: list[dict[str, Any]],
        headers: list[str] | None = None,
        exclude_headers: list[str] | None = None,
        case_sensitive: bool = False,
        set_focus: bool = False,
    ):
        """
        Fills or Overwrites GuiTableControl table with the provided data. Each item in the data must be of type {
         header_name: value_to_set_or_overwrite
        }.
        This functions handles pagination, dismisses popups, checks for the status bar for any errors, after each page.

        Parameters
        ----------
        data : list[dict[str, Any]]
            Data to fill/overwrite the table with.
        headers : list[str] | None, optional
            Select the headers to fill/overwrite, the headers must match and be consistent the keys in the data. If None, it will consider all the headers in the table to fill/overwrite, by default None
        exclude_headers : list[str] | None, optional
            List of headers to exclude. If None, no headers are excluded, by default None
        set_focus : bool, optional
            Focus on the element before filling/overwriting, by default False
        case_sensitive: bool, optional
            Whether to match headers case-sensitively, by default False. If False, then the keys in the data and sap table header names are matched case-insensitively.

        Raises
        ------
        ValueError
            If both headers and exclude_headers are specified.
        ValueError
            If provided data is empty.
        """
        if headers and exclude_headers:
            raise ValueError("Cannot specify both 'headers' and 'exclude_headers'.")

        if not data:
            raise ValueError("Provided Data is Empty.")

        self.headers = self.get_table_headers(
            headers,
            exclude_headers,
            not case_sensitive,
        )

        logger.debug(f"Table headers: {self.headers}")
        if not case_sensitive:
            # Make all the keys in the data to lower case
            data = [{k.lower(): v for k, v in row.items()} for row in data]

        # Check if table is empty (scroll max == 0 usually implies empty or single page)
        is_table_empty = self.VerticalScrollbar.Maximum == 0
        logger.info(
            f"Filling table {self.id} ({len(data)} rows). Mode: {'Fill empty' if is_table_empty else 'Overwrite'}"
        )
        # Reset scroll position for overwriting existing data
        if not is_table_empty:
            self.VerticalScrollbar.Position = 0
            self._refresh_table()

        # Choose pagination strategy based on whether the table is empty (filling) or not empty (overwriting)
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
        self.__parent_class__.press_enter()
        self.__parent_class__.dismiss_popups()
        self.__parent_class__.raise_if_error_dialog(
            exception=SAPTableConfigurationError,
            message="Error while filling table:",
        )
        self.__parent_class__.raise_for_status()

    def _upate_row_cells(
        self,
        row_idx: int,
        row: dict[str, Any],
        page: int,
        set_focus: bool = False,
    ):
        # Note: I chose to iterate over colum_map, because length of column_map might be lesser than the length of row
        for col, col_idx in self.headers.items():
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
        self.__parent_class__.send_vkey(pagination_key)
        self.__parent_class__.dismiss_popups()
        self.__parent_class__.raise_if_error_dialog(
            exception=SAPTableConfigurationError,
            message="Error while filling table:",
        )
        self.__parent_class__.raise_for_status()

    def _refresh_table(self):
        """
        Refreshes the underlying GuiTableControl object reference
        """
        self._com_element = self.__parent_class__.find_by_id(self.id)
