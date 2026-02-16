import logging
import re
from typing import Optional

from .connection import SAPConnectionManager
from .constants import ControlID, GuiObject, VKey
from .exceptions import (
    SAPElementNotFound,
    SAPLoginError,
    SAPStatusBarError,
    SAPTransactionError,
)
from .launcher import SAPLauncher
from .models import LoginElements, StatusbarInfo
from .ui import GuiTableControl, GuiVComponent

logger = logging.getLogger(__name__)


class SAPGuiEngine:
    WINDOW_TITLE = "SAP Logon 770"
    EXECUTABLE_PATH = r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"

    def __init__(
        self,
        connection_name: str,
        window_title: Optional[str] = None,
        executable_path: Optional[str] = None,
    ):
        if not window_title:
            window_title = self.WINDOW_TITLE
        if not executable_path:
            executable_path = self.EXECUTABLE_PATH

        self._launcher = SAPLauncher(executable_path, window_title)
        self._conn_manager = SAPConnectionManager()

        self._launcher.launch()
        self._conn_manager.open_connection(connection_name)

    @property
    def session(self):
        """Gets the underlying native SAP GUI session object."""
        return self._conn_manager.session

    def close_session(self):
        return self._conn_manager.close_session()

    def find_by_id(
        self, id: str, raise_error: bool = True
    ) -> Optional["GuiVComponent"]:
        """
        Finds a GUI component by its SAP ID

        Parameters
        ----------
        id : str
            The ID of the GUI element
        raise_error : bool, optional
            If True, raises SAPElementNotFound if missing, by default True

        Returns
        -------
        Optional['GuiVComponent']
            GuiVComponent wrapper or None if not found (and raise_error is False)

        Raises
        ------
        SAPElementNotFound
            If the element is not found and raise_error is True
        """
        element = self.session.findById(id, False)  # False = don't raise com error

        if element is None:
            if raise_error:
                raise SAPElementNotFound(f"The element with ID: {id} was not found.")

            return None

        if element.type == GuiObject.TABLE_CONTROL:
            return GuiTableControl(element, id, self)

        return GuiVComponent(element, self)

    def send_vkey(
        self, key: VKey | int, window_index: int = 0, repeat_count: int = 1
    ) -> None:
        """Sends a VKey to a specific SAP window

        Parameters
        ----------
        key : VKey | int
            The virutal key to send
        window_index : int, optional
            Index of the SAP window, by default 0
        repeat_count : int, optional
            Number of times to send the key, by default 1

        Raises
        ------
        SAPElementNotFound
            If the window is not found
        """

        wnd_id = f"wnd[{window_index}]"
        wnd = self.session.findById(wnd_id, False)
        if wnd:
            val = key.value if isinstance(key, VKey) else key
            for _ in range(repeat_count):
                wnd.sendVKey(val)
        else:
            raise SAPElementNotFound(f"Window {wnd_id} not found to send key.")

    def press_enter(self, window_index: int = 0) -> None:
        """Helper method to send the ENTER virtualkey to a window."""
        return self.send_vkey(VKey.ENTER, window_index)

    def dismiss_popups(self, key: VKey = VKey.ENTER, window_index: int = 1) -> None:
        """
        Dismisses popup dialogs until there are no popups by sending a specific key to the popup window

        Parameters
        ----------
        key : VKey, optional
            The key to send to dismiss the popup, by default VKey.ENTER
        window_index : int, optional
            The index of the popup dialog window, by default 1
        """
        window_id = f"wnd[{window_index}]"

        while True:
            wnd = self.find_by_id(window_id, raise_error=False)
            if not wnd:
                logger.debug("No more popup dialogs found. Stopping.")
                break

            if wnd.type == GuiObject.MODAL_WINDOW and wnd.isPopupDialog:
                logger.debug(
                    f"Dismissing popup dialog:\ntitle: {wnd.text}\ntext: {wnd.PopupDialogText}"
                )
                wnd.send_vkey(key)
            else:
                logger.debug("No more popup dialogs found. Stopping.")
                break

    def get_statusbar_info(self) -> StatusbarInfo:
        """
        Retrieves current status bar details.

        Returns
        -------
        StatusbarInfo
            A dictionary containing the status bar information.

        Raises
        ------
        SAPElementNotFound
            If the status bar is not found
        """
        sbar = self.find_by_id(ControlID.STATUS_BAR, False)
        if not sbar:
            raise SAPElementNotFound("Status bar not found")

        return {
            "id": sbar.MessageId,
            "text": sbar.text,
            "type": sbar.MessageType,
            "number": sbar.MessageNumber,
            "is_popup": sbar.MessageAsPopup,
            "parameter": sbar.MessageParameter,
        }

    def raise_for_status(
        self,
        exception: Exception = SAPStatusBarError,
        message: str | None = None,
    ) -> StatusbarInfo:
        """Checks the status bar for error message type and raises the given exception

        Parameters
        ----------
        exception : Exception, optional
            The exception object to raise, by default SAPError
        message : str | None, optional
            Optional message to prepend to the error message, by default None
        """
        sbar = self.get_statusbar_info()
        if not sbar["type"] == "E":
            return sbar

        error_message = f"{message}: {sbar['text']}" if message else sbar["text"]
        raise exception(error_message)

    def get_document_number(self) -> Optional[int]:
        """
        Extracts document number from status bar when document is created successfully. Particularly useful when creating documents in VA01 transaction. (e.g., 'Document 1234 saved').

        Returns
        -------
        Optional[int]
            Extracted document number or None if not found/parseable.
        """
        info = self.get_statusbar_info()
        text = info.get("text")
        if not text:
            return None

        # Regex for standalone digits
        match = re.search(r"\b\d+\b", text)
        if match:
            return int(match.group(0))

        return None

    def raise_if_error_dialog(
        self,
        window_index: int = 1,
        exception=SAPTransactionError,
        message="Error dialog detected",
    ) -> None:
        wnd = self.find_by_id(f"wnd[{window_index}]", raise_error=False)

        if not wnd:
            return

        is_popup = wnd.isPopupDialog

        if is_popup:
            return

        # It's a modal window but NOT a dismissable popup
        title = str(wnd.text).strip()
        dlg_text = str(wnd.PopupDialogText).strip()
        error_message = f"{title}: {dlg_text}" if dlg_text else title
        raise exception(f"{message}: {error_message}")

    def maximize(self) -> None:
        """Maximizes the main window."""
        self.find_by_id(GuiObject.MAIN_WINDOW).maximize()

    def bring_window_to_front(self) -> None:
        """Brings the main SAP window to the foreground."""
        wnd = self.find_by_id(ControlID.MAIN_WINDOW)
        wnd.iconify()
        wnd.maximize()

    def start_transaction(self, tcode: str) -> None:
        """
        Starts a new transaction. Ends any current transaction first.

        Parameters
        ----------
        tcode : str
            Code of the transaction to start.

        Raises
        ------
        SAPTransactionError
            If transaction code does not exist or Function is not possible.

        """
        logger.debug(f"Starting transaction: {tcode}")
        self.session.StartTransaction(tcode)

        # Check if tcode was valid
        status = self.get_statusbar_info()
        if status and "does not exist" in status["text"].lower():
            raise SAPTransactionError(f"Transaction {tcode} failed: {status['text']}")

    def end_transaction(self) -> None:
        """Ends the current SAP transaction. (equivalent to /n)"""
        self.session.EndTransaction()

    def login(
        self,
        username: str,
        password: str,
        terminate_other_sessions: bool = True,
        elements: LoginElements = LoginElements(),
    ) -> bool:
        """Performs SAP login with the provided credentials. It handles multiple login attempts, incorrect password attempts, terminates other sessions logged in other computers.

        Parameters
        ----------
        username : str
        password : str
        terminate_other_sessions : bool, optional
            If true, terminates other sessions logged in other computers, by default True
        elements : LoginElements, optional
            Login element mappings, by default LoginElements()

        Returns
        -------
        bool
            True if login was successful or user already logged in

        Raises
        ------
        SAPLoginError
            If login fails
        """
        user_field = self.find_by_id(elements.username, raise_error=False)
        if not user_field:
            logger.info("Login screen not found. Assuming user is already logged in.")
            return True

        logger.info(f"Logging in as {username}...")
        user_field.text = username
        self.find_by_id(elements.password).text = password
        self.press_enter()

        # Check for immediate login errors (e.g., invalid credentials)
        status = self.raise_for_status(SAPLoginError, message="Login failed")

        # Handle multi-logon
        if status and "already logged on" in (status["text"] or "").lower():
            logger.info("Multi-logon detected")
            if not terminate_other_sessions:
                raise SAPLoginError("User already logged on in some other session.")

            logger.info("Terminating other sessions...")
            try:
                rb = self.find_by_id(
                    ControlID.TERMINATE_OTHER_SESSIONS_RADIO, raise_error=False
                )
                if rb:
                    rb.select()

                self.press_enter(1)
            except Exception as e:
                logger.warning(
                    f"Could not find multi-logon terminate radio button, attempting default enter: {e}"
                )
                self.press_enter(1)

        # Dismiss any other popup dialogs that may appear
        self.dismiss_popups()
        return True
