import logging
import polars as pl
from pathlib import Path
from typing import Any
from sap_gui_engine.vkey import VKey
from sap_gui_engine.objects import SAPGuiElement, GuiTableControl
from sap_gui_engine.mappings.login import DEFAULT_LOGIN_ELEMENTS, LoginScreenElements
from sap_gui_engine.exceptions import LoginError
from sap_gui_engine.managers import (
    SAPConnectionManager,
    SAPWindowManager,
    SAPLauncher,
)

logger = logging.getLogger(__name__)


class SAPGuiEngine:
    def __init__(
        self,
        connection_name: str,
        window_title: str,
        executable_path: str | Path,
    ):
        if isinstance(executable_path, str):
            executable_path = Path(executable_path)

        self._launcher = SAPLauncher(executable_path, window_title)
        self._connection_manager = SAPConnectionManager(connection_name, window_title)
        self._launcher.launch_sap()
        self.open_connection(connection_name)

    @property
    def connection_name(self) -> str:
        """Get the connection name."""
        return self._connection_manager.connection_name

    @property
    def session(self):
        """Get the current SAP session."""
        return self._connection_manager.session

    @property
    def is_connected(self) -> bool:
        return self._connection_manager.is_connected()

    def open_connection(self, connection_name: str) -> bool:
        """Tries to connect to existing open connection, if not found then opens new one."""
        self._connection_manager.open_connection(connection_name)
        logger.info("Connection opened successfully.")
        self._window_manager = None
        self._window_manager = SAPWindowManager(self.session)
        self._window_manager.maximize()
        return True

    def close_connection(self) -> None:
        """Closes the current SAP connection."""
        self._connection_manager.close_connection()

    def maximize(self, window: int = 0) -> None:
        """Maximizes the specified SAP window."""
        self._window_manager.maximize(window)

    def sendVKey(self, key: VKey, window: int = 0, times: int = 1) -> bool:
        """Sends a virtual key to a window."""
        return self._window_manager.send_vkey(key, window, times)

    def send_enter(self, window: int = 0, times: int = 1) -> bool:
        """Sends enter key to a window. This is a convenFience method for send_vkey(VKey.ENTER, window), as enter is used very frequently."""
        return self._window_manager.send_vkey(VKey.ENTER, window, times)

    def findById(self, id: str) -> SAPGuiElement:
        """Finds an SAP element by ID."""
        return self._window_manager.find_element(id)

    def get_status_info(self) -> dict[str, Any] | None:
        """Gets current status bar information."""
        return self._window_manager.get_status_info()

    def get_document_number(self) -> str:
        """Extracts document number from status bar when document is created successfully using va01 transaction."""
        return self._window_manager.get_document_number()

    def start_transaction(self, tcode: str, new_transaction: bool = True) -> bool:
        """Starts a SAP transaction."""
        return self._window_manager.start_transaction(tcode, new_transaction)

    def login(
        self,
        username: str,
        password: str,
        terminate_other_sessions: bool = True,
        login_screen_elements: LoginScreenElements = DEFAULT_LOGIN_ELEMENTS,
    ) -> bool:
        """Performs SAP login with provided credentials only if it finds login elements, with all possible exceptions/scenarios handled."""
        try:
            self.findById(login_screen_elements.username).text = username
            self.findById(login_screen_elements.password).text = password
            self.sendVKey(VKey.ENTER)
        except Exception as e:
            # Control not found, this means either the login screen is not open or the user is already logged on
            logger.warning(f"User already logged on: {e}")
            return True

        status = self.get_status_info()
        if status and status["type"] == "E":
            logger.error(f"Login failed with status: {status}")
            logger.error(status["text"])
            raise LoginError(status["text"])

        logger.info("User login successful")

        # Check if user is already logged on in some other instance
        if status and "already logged on" in status["text"].lower():
            logger.info(status["text"])
            if not terminate_other_sessions:
                raise LoginError(status["text"])

            logger.info("Terminating other sessions")
            self.findById("wnd[1]/usr/radMULTI_LOGON_OPT1").select()
            self.sendVKey(VKey.ENTER, window=1)

        # Check for number of attempts dialog that appears after incorrect login credentials, and press enter
        try:
            if str(self.findById("wnd[1]").text).lower() == "information":
                self.sendVKey(VKey.ENTER, window=1)
        except Exception:
            # The popup dialog did not appear, so we can continue
            pass

        return True

    def handle_popups_until_none(self, key: VKey = VKey.ENTER):
        """Handles all popup dialogs by sending specified vkey until none are left. Assuming popup dialog is wnd[1]."""
        while True:
            try:
                self.findById("wnd[1]")
                self.sendVKey(key=key, window=1)
            except Exception as e:
                # No popup dialogs found, we can continue
                logger.info(f"No more popup dialogs found: {e}")
                break

    def fill_table(
        self,
        table_id: str,
        df: pl.DataFrame,
        filter_columns: list[str] | None = None,
        exclude_columns: list[str] | None = None,
    ):
        """
        Populates a specified SAP GUI table with rows from a Polars DataFrame.

        The function iterates through the DataFrame and maps its columns to the SAP table's
        column titles. The mapping logic is case-insensitive and trims whitespace from titles
        to ensure reliable matching. It handles pagination automatically by sending the ENTER
        key when the visible rows are filled.

        Columns in the DataFrame that do not have a corresponding title in the SAP table are
        silently ignored. Columns in the SAP table that are not present in the DataFrame will
        remain empty.

        Args:
            table_id : The ID of the SAP table element to fill.

            df: The Polars DataFrame containing the data. The DataFrame should have columns that correspond to the titles in the
                SAP table.

            filter_columns (Optional): If provided, restricts data entry to only the specified SAP table column titles. This is
                useful for selectively updating a subset of columns. Cannot be used with `exclude_columns`.

            exclude_columns (Optional): If provided, prevents data entry into the specified SAP table column titles. This is
                useful for avoidingupdates to certain fields. Cannot be used with `filter_columns`
        Returns:
            None: The function performs an action (modifying the SAP GUI) and does not return a value.

        Raises:
            ValueError: If both `filter_columns` and `exclude_columns` are provided
        """

        if filter_columns and exclude_columns:
            raise ValueError(
                "Both filter_columns and exclude_columns cannot be used together"
            )

        table = self.session.findById(table_id)
        if table.type != "GuiTable":
            raise ValueError(f"Element {table_id} is not a table")

        table = GuiTableControl(table)
        table.set_scroll_position(0)
        # Refresh table
        table = GuiTableControl(self.session.findById(table_id))

        total_rows = df.height
        if total_rows == 0:
            logger.info("Data contains no items")
            return

        col_idx_map = table.get_column_idx_map(
            filter_columns=filter_columns, exclude_columns=exclude_columns
        )
        visible_rows = table.visible_row_count
        i = 0
        page = 0
        for row in df.iter_rows(named=True):
            start_row = 0 if page == 0 else 1
            current_row = start_row + (i % visible_rows)

            # Check if we need to move to the next page
            if (current_row > 0) and current_row % visible_rows == 0:
                page += 1
                self.send_enter()
                # Handle all popup dialogs
                self.handle_popups_until_none()
                # Refresh table
                table = GuiTableControl(self.session.findById(table_id))

            # Fill row data
            for col, value in row.items():
                if col in col_idx_map:
                    col_idx = col_idx_map[col]
                    text = "" if value is None else str(value)
                    table.get_cell(current_row, col_idx).text = text

            i += 1

        # After filling all the rows, final commit to save changes
        self.send_enter()
        # Handle all popup dialogs
        self.handle_popups_until_none()
