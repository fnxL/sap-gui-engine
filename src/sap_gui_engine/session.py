import logging
from typing import Optional, TypedDict

from sap_gui_engine.constants import ControlID, GuiObject, VKey
from sap_gui_engine.exceptions import (
    SAPElementNotFound,
    SAPStatusBarError,
    SAPTransactionError,
)
from sap_gui_engine.objects import GuiVComponent

logger = logging.getLogger(__name__)


class StatusbarInfo(TypedDict):
    """Structure for SAP Status Bar information."""

    id: str
    text: str | None
    type: str
    number: str | None
    is_popup: bool
    parameter: str


class SAPSession:
    def __init__(self, com_session):
        self._com_session = com_session

    @property
    def session(self):
        """Gets the underlying native SAP GUI session object."""
        return self._com_session

    def close_session(self):
        pass

    def find_by_id(
        self,
        id: str,
        raise_error: bool = True,
    ) -> Optional[GuiVComponent]:
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
        element = self._com_session.findById(id, False)  # False = don't raise com error

        if element is None:
            if raise_error:
                raise SAPElementNotFound(f"The element with ID: {id} not found")
            return None

        return GuiVComponent(element)

    def send_vkey(self, key: VKey | int, window_index: int = 0, repeat_count: int = 1):
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
        wnd = self._com_session.findById(wnd_id, False)
        if wnd:
            val = key.value if isinstance(key, VKey) else key
            for _ in range(repeat_count):
                wnd.sendVKey(val)
        else:
            raise SAPElementNotFound(f"Window {wnd_id} not found to send key.")

    def press_enter(self, window_index: int = 0, repeat_count: int = 1):
        """Helper method to send the ENTER virtualkey to a window."""
        return self.send_vkey(
            VKey.ENTER, window_index=window_index, repeat_count=repeat_count
        )

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
