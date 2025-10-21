import logging
from pathlib import Path
from typing import Any

from sap_gui_engine.vkey import VKey
from sap_gui_engine.objects import SAPGuiElement
from sap_gui_engine.mappings.login import DEFAULT_LOGIN_ELEMENTS, LoginScreenElements
from sap_gui_engine.exceptions import LoginError, TransactionError
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

    def findById(self, id: str) -> SAPGuiElement:
        """Finds an SAP element by ID."""
        return self._window_manager.find_element(id)

    def get_status_info(self) -> dict[str, Any] | None:
        """Gets current status bar information."""
        return self._window_manager.get_status_info()

    def get_document_number(self) -> str:
        """Extracts document number from status bar when document is created successfully using va01 transaction."""
        return self._window_manager.get_document_number()

    def login(
        self,
        username: str,
        password: str,
        terminate_other_sessions: bool = True,
        login_screen_elements: LoginScreenElements = DEFAULT_LOGIN_ELEMENTS,
    ) -> bool:
        """Performs SAP login with provided credentials with all possible exceptions handled."""
        self.findById(login_screen_elements.username).set_text(username)
        self.findById(login_screen_elements.password).set_text(password)
        self.sendVKey(VKey.ENTER)

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

    def start_transaction(self, tcode: str, new_transaction: bool = True) -> bool:
        """Starts a SAP transaction."""
        if new_transaction:
            self._connection_manager.session.StartTransaction(tcode)
        else:
            self._connection_manager.session.SendCommand(tcode)

        status = self.get_status_info()
        if status and "does not exist" in status["text"].lower():
            logger.error(status["text"])
            raise TransactionError(status["text"])

        return True
