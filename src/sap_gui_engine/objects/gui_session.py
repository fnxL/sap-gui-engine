import logging
from typing import Optional, Type, overload

from sap_gui_engine.constants import ControlID, GuiObject, VKey
from sap_gui_engine.exceptions import (
    SAPElementNotFound,
    SAPStatusBarError,
    SAPTransactionError,
)

from .gui_table_control import GuiTableControl
from .gui_vcomponent import GuiVComponent
from .session_info import SessionInfo
from .statusbar_msg import StatusbarMsg

logger = logging.getLogger(__name__)


class GuiSession:
    """
    A wrapper class for SAP GUI COM Session objects that provides convenient methods
    for common operations while delegating unknown attributes and methods to the
    underlying COM session object.

    This class implements attribute delegation, meaning that if a requested attribute
    or method is not found in this class, it will be looked up in the underlying
    _com_session object. Methods defined in this class take precedence over those
    in the _com_session object.
    """

    def __init__(self, com_session):
        self._com_session = com_session

    def __getattr__(self, name):
        """
        Delegate attribute access to the underlying _com_session object.
        """
        return getattr(self._com_session, name)

    @property
    def session(self):
        """Gets the underlying native SAP GUI session object."""
        return self._com_session

    def close(self):
        """
        Closes the current session.
        """
        self._com_session.SendCommand("/i")
        # If this is not the last session, the session closes here immediately and _com_session object becomes unknown, so find_by_id will throw an
        try:
            dlg = self.find_by_id("wnd[1]/usr/btnSPOP-OPTION1", False)
            if dlg:
                dlg.click()
        except Exception:
            # This is expected if the session is not the last one.
            pass
        return

    @overload
    def find_by_id(
        self, id: str, raise_error: bool = True
    ) -> GuiVComponent | GuiTableControl: ...

    @overload
    def find_by_id(
        self, id: str, raise_error: bool = False
    ) -> Optional["GuiVComponent"]: ...

    def find_by_id(
        self,
        id: str,
        raise_error: bool = True,
    ) -> Optional[GuiVComponent | GuiTableControl]:
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

        if element.Type == GuiObject.TABLE_CONTROL:
            return GuiTableControl(element, id, self)

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

    def dismiss_popups(
        self,
        key: VKey = VKey.ENTER,
        window_index: int = 1,
        limit: int | None = None,
    ) -> None:
        """
        Dismisses popup dialogs until there are no popups or limit is reached by sending a specific key to the popup window

        Parameters
        ----------
        key : VKey, optional
            The key to send to dismiss the popup, by default VKey.ENTER
        window_index : int, optional
            The index of the popup dialog window, by default 1
        limit : int | None, optional
            The maximum number of popups to dismiss, by default None
        """
        window_id = f"wnd[{window_index}]"
        count = 0
        while True:
            if limit and count >= limit:
                logger.debug(f"Reached limit of dismissing {limit} popups. Stopping.")
                return

            wnd = self.find_by_id(window_id, raise_error=False)
            if not wnd:
                logger.debug("No more popup dialogs found. Stopping.")
                return

            if wnd.type == GuiObject.MODAL_WINDOW and wnd.isPopupDialog:
                logger.debug(
                    f"Dismissing popup dialog:\ntitle: {wnd.text}\ntext: {wnd.PopupDialogText}"
                )
                wnd.send_vkey(key)
            else:
                logger.debug("No more popup dialogs found. Stopping.")
                return

    def get_statusbar_msg(self) -> StatusbarMsg:
        """
        Retreives the current status bar message.

        Returns
        -------
        StatusbarMsg
            The StatusbarMsg dataclass

        Raises
        ------
        SAPElementNotFound
            If the statusbar is not found in the window
        """
        sbar = self.find_by_id(ControlID.STATUS_BAR, False)
        if not sbar:
            raise SAPElementNotFound("Status bar not found")

        return StatusbarMsg(
            id=sbar.MessageId,
            number=sbar.MessageNumber,
            text=sbar.text,
            type=sbar.MessageType,
            has_longtext=sbar.MessageHasLongtext,
            is_popup=sbar.MessageAsPopup,
        )

    def raise_for_status(
        self,
        message: str | None = None,
        exception: Type[Exception] = SAPStatusBarError,
    ) -> StatusbarMsg:
        """Checks the status bar for error message type and raises the given exception

        Parameters
        ----------
        exception : Exception, optional
            The exception object to raise, by default SAPError
        message : str | None, optional
            Optional message to prepend to the error message, by default None
        """
        sbar = self.get_statusbar_msg()
        if not sbar.type == "E":
            return sbar

        error_message = f"{message}: {sbar.text}" if message else sbar.text
        raise exception(error_message)

    def raise_if_error_dialog(
        self,
        window_index: int = 1,
        exception: Type[Exception] = SAPTransactionError,
        message="Error dialog detected",
    ) -> None:
        """
        Raises an exception if the there is a ModalWindow which is not a popup dialog

        Parameters
        ----------
        window_index : int, optional
            The window index to check, by default 1
        exception : Type[Exception], optional
            The exception object to raise, by default SAPTransactionError
        message : str, optional
            Optional message to prepend to the error message, by default "Error dialog detected"

        Raises
        ------
        exception
            If the window is a modal window and not a popup dialog
        """
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

    def start_transaction(self, tcode: str) -> bool:
        """
        Starts a new transaction. Ends any current transaction first.

        Parameters
        ----------
        tcode : str
            Code of the transaction to start.

        Returns
        -------
        bool
            True if the transaction was started successfully.

        Raises
        ------
        SAPTransactionError
            If transaction code does not exist or Function is not possible.

        """
        logger.debug(f"Starting transaction: {tcode}")
        self._com_session.StartTransaction(tcode)

        # Check if tcode was valid
        status = self.get_statusbar_msg()
        if status.text and "does not exist" in status.text.lower():
            raise SAPTransactionError(f"Transaction {tcode} failed: {status.text}")

        return True

    def end_transaction(self) -> None:
        """Ends the current SAP transaction. (equivalent to /n)"""
        self._com_session.EndTransaction()

    def get_session_info(self) -> SessionInfo:
        """
        Get current session info

        Returns
        -------
        SessionInfo
            Details of the current session
        """
        info = self._com_session.info
        return SessionInfo(
            application_server=info.ApplicationServer,
            client=info.Client,
            codepage=info.Codepage,
            flushes=info.Flushes,
            group=info.Group,
            gui_codepage=info.GuiCodepage,
            i18n_mode=info.I18nMode,
            iterpretation_time=info.InterpretationTime,
            is_low_speed_connection=info.IsLowSpeedConnection,
            language=info.Language,
            message_server=info.MessageServer,
            program=info.Program,
            response_time=info.ResponseTime,
            round_trips=info.RoundTrips,
            screen_number=info.ScreenNumber,
            scripting_mode_read_only=info.ScriptingModeReadOnly,
            scripting_mode_recording_disabled=info.ScriptingModeRecordingDisabled,
            session_number=info.SessionNumber,
            system_name=info.SystemName,
            system_session_id=info.SystemSessionId,
            transaction=info.Transaction,
            ui_guideline=info.UI_GUIDELINE,
            user=info.User,
        )
