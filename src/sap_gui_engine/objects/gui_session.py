import logging
from typing import TypedDict, Any
from pathlib import Path
from ..exceptions import TransactionError, TableConfigurationError
from .gui_component import GuiComponent
from .gui_table_control import GuiTableControl
from ..mappings import VKey
from .utils import get_column_idx_map

logger = logging.getLogger(__name__)

IMAGE_FORMAT_MAP = {
    "bmp": 0,
    "jpg": 1,
    "png": 2,
    "gif": 3,
    "tiff": 4,
}


class StatusInfo(TypedDict):
    id: str
    text: str | None
    type: str
    number: str | None
    is_popup: bool
    parameter: str


class GuiSession:
    def __init__(self, session: Any):
        self._session = session

    def maximize(self):
        """Maximizes the main SAP window"""
        try:
            self._session.findById("wnd[0]").maximize()
        except Exception as e:
            raise RuntimeError(f"Error maximizing window 0: {str(e)}")

    def start_transaction(self, tcode: str) -> bool:
        """
        Starts a new SAP transaction.
        Args:
            tcode: Transaction code to start.

        Returns:
            True if transaction started successfully

        Raises:
            TransactionError: If transaction code does not exist or Function is not possible.

        Note: This will end any existing transaction without saving your work. Use this with caution.
        """
        self._session.StartTransaction(tcode)

        status = self.get_status_info()
        if status and "does not exist" in status["text"].lower():
            logger.error(status["text"])
            raise TransactionError(status["text"])

        return True

    def end_transaction(self) -> bool:
        """Ends the current SAP transaction. Calling this function has the same effect as SendCommand("/n")."""
        self._session.EndTransaction()
        return True

    def findById(self, id: str):
        try:
            if "tbl" in id:
                last_part = id.split("/")[-1]
                if "tbl" in last_part:
                    return GuiTableControl(self._session.findById(id))

            return GuiComponent(self._session.findById(id))
        except Exception:
            raise ValueError(f"The control {id} could not be found.")

    def sendVKey(self, key: VKey, window: int = 0, times: int = 1) -> bool:
        """
        Sends a virtual key to a window.
        Args:
            key: Virtual key to send.
            window: Window to send the key to.
            times: Number of times to send the key.

        Returns:
            True if key sent successfully.

        Raises:
            RuntimeError: If key could not be sent.
        """
        try:
            for _ in range(times):
                self._session.findById(f"wnd[{window}]").sendVKey(key.value)
            return True
        except Exception as e:
            raise RuntimeError(f"Error sending vkey {key} to window {window}: {str(e)}")

    def press_enter(self, window: int = 0) -> bool:
        """Sends the ENTER virtualkey to a window."""
        return self.sendVKey(VKey.ENTER, window)

    def get_status_info(self) -> StatusInfo | None:
        """Gets current status bar information."""
        try:
            status_bar = self._session.findById("wnd[0]/sbar")
            return {
                "id": status_bar.MessageId,
                "text": status_bar.text,
                "type": status_bar.MessageType,
                "number": status_bar.MessageNumber,
                "is_popup": status_bar.MessageAsPopup,
                "parameter": status_bar.MessageParameter,
            }
        except Exception as e:
            logger.error(f"Error getting status bar information: {str(e)}")
            return None

    def get_document_number(self) -> str | None:
        """Extracts document number from status bar when document is created successfully using va01 transaction."""
        status = self.get_status_info()
        try:
            return status["text"].split(" ")[3]
        except Exception as e:
            logger.error(f"Error getting document number: {status.get('text')}")
            logger.error(str(e))
            return None

    def take_screenshot(
        self, file_path: str | Path, window: int = 0, format: str = "png"
    ):
        """Takes a screenshot of the specified window and saves it to the specified file path."""
        format_int_value = IMAGE_FORMAT_MAP.get(format.lower())
        if not format_int_value:
            raise ValueError(f"Invalid image format: {format}")
        try:
            self._session.findById(f"wnd[{window}]").HardCopy(str(file_path), format)
        except Exception as e:
            raise RuntimeError(f"Error taking screenshot: {str(e)}")

    def check_for_error_dialog(self, window: int = 1) -> str | None:
        try:
            wnd = self._session.findById(f"wnd[{window}]")
            if wnd.type != "GuiModalWindow" or not wnd.isPopupDialog:
                dlg_text = str(wnd.PopupDialogText).strip()
                wnd_title = str(wnd.text).strip()
                if dlg_text:
                    return dlg_text
                return wnd_title
            return None
        except Exception as e:
            logger.error(f"Error finding window {window}: {str(e)}")
            return False

    def dismiss_popups(self, key: VKey = VKey.ENTER, window: int = 1):
        """
        Continuously dismisses popup dialogs by sending a specified virtual key (vkey)
        to specified window until no more popups appear.

        Note: This method only works if the window is GuiModalWindow type and isPopupDialog property is True.

        Args:
            key: Virtual key to send to dismiss the popup dialog.
            window: Window to send the key to.
        """

        # Early return if window is not a popup dialog
        try:
            wnd = self._session.findById(f"wnd[{window}]")
            if wnd.type != "GuiModalWindow" or not wnd.isPopupDialog:
                return
            wnd.sendVKey(key.value)
        except Exception as e:
            logger.error(f"Error finding window {window}: {str(e)}")
            return

        while True:
            try:
                wnd = self._session.findById(f"wnd[{window}]")
                if wnd.type != "GuiModalWindow" or not wnd.isPopupDialog:
                    logger.debug(f"Not a popup dialog: {wnd.text}. Stopping.")
                    return
                logger.debug(f"Dismissing popup dialog: {wnd.text}")
                wnd.sendVKey(key.value)

            except Exception as e:
                # No popup dialogs found, we can continue
                logger.error(
                    f"No more popup dialogs found: {str(e)} | window: {window}"
                )
                return

    def fill_table(
        self,
        id: str,
        data: list[dict[str, Any]],
        columns: list[str] | None = None,
        exclude_columns: list[str] | None = None,
        set_focus: bool = False,
    ):
        """
        Populates a specified SAP GUI table with the data from a list of dictionaries.

        Each dictionary in `data` represents a single table row, where keys correspond
        to column titles and values to cell contents. Column name matching is case-insensitive.
        Columns that do not exist in the SAP table are ignored, and columns not present
        in a row's dictionary remain empty.

        The function automatically handles pagination by sending the ENTER key when the
        visible portion of the table is filled, and any popup dialogs that may appear.

        Args:
            id (str):
            The unique ID of the SAP `GuiTableControl` element to populate.

            data (list[dict[str, Any]]):
                A list of dictionaries, each representing one row of data to fill into
                the table.

            columns (list[str], optional):
                If provided, only these columns will be updated. This allows partial updates
                of the table. Cannot be used together with `exclude_columns`.

            exclude_columns (list[str], optional):
                If provided, these columns will be skipped when populating data.
                Cannot be used together with `columns`.

            set_focus (bool, optional):
                If True, the cell would get focused first before setting the value. Defaults to False.
                This is useful when you want the cell to get into viewport automatically (horizontally scroll to it automatically) for visual feedback only before setting the value.

        Raises:
            ValueError:
                If both `columns` and `exclude_columns` are provided.
            ValueError:
                If the element specified by `id` is not a `GuiTableControl`.

        Notes:
            - Column name comparisons are case-insensitive.
            - Columns or keys that do not match existing table columns are silently ignored.
            - Pagination is handled automatically via simulated ENTER key presses.
        """

        if columns and exclude_columns:
            raise ValueError("Both columns and exclude_columns cannot be used together")

        if not data:
            raise ValueError("Data contains no items")

        table = self._session.findById(id)

        if table.type != "GuiTableControl":
            raise ValueError(f"Element {id} is not a table")

        total_rows = len(data)
        logger.info(f"Total rows: {total_rows}")

        column_map = get_column_idx_map(table, columns, exclude_columns)
        visible_rows = table.VisibleRowCount
        logger.info(f"Visible rows: {visible_rows}")

        # The current_row_idx should start from 0 if it is the first page, otherwise it should start from 1 always
        page = 0
        current_row_idx = 0
        for row in data:
            # Note: I chose to iterate over colum_map, because length of column_map might be lesser than the length of row
            logger.info(f"Current row index: {current_row_idx} | page: {page}")

            for col, col_idx in column_map.items():
                # For each column in the SAP table, check if it exists in the row. Skip if not.
                if col not in row:
                    continue

                cell = table.GetCell(current_row_idx, col_idx)
                if set_focus:
                    cell.setFocus()

                # Set the cell value if it is not None
                if row.get(col) is not None:
                    # Check if the cell is a combobox and convert it to a GuiComponent type to support setting the combobox values
                    if cell.type == "GuiComboBox":
                        cell = GuiComponent(cell)

                    cell.text = str(row[col]).strip()

            # If we have filled the last row of the current page, we want to go the next page
            if current_row_idx == visible_rows - 1:
                logger.info("Moving to next page")
                self.press_enter()
                self.dismiss_popups()
                # Check for wnd[1] which is not a popup dialog (F8)
                # TODO: Abstract this into a function

                error_dialog = self.check_for_error_dialog()
                if error_dialog:
                    raise TableConfigurationError(
                        f"Error while filling table: {error_dialog}"
                    )
                table = self._session.findById(id)
                page += 1
                current_row_idx = 1
                continue

            current_row_idx += 1

        # Afte filling all the rows, press_enter final time to reflect changes
        self.press_enter()
        self.dismiss_popups()
