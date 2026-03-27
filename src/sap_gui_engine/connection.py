import logging
import time
from dataclasses import dataclass

import pythoncom
import win32com.client as win32

from sap_gui_engine.constants import ControlID
from sap_gui_engine.exceptions import SAPConnectionError, SAPLoginError
from sap_gui_engine.objects import GuiSession
from sap_gui_engine.utils import launch_application
from sap_gui_engine.utils.lock_manager import get_global_lock_manager

logger = logging.getLogger(__name__)


@dataclass
class SAPLoginScreenElements:
    username: str = "wnd[0]/usr/txtRSYST-BNAME"
    password: str = "wnd[0]/usr/pwdRSYST-BCODE"


MAX_SESSIONS = 6


class SAPConnection:
    def __init__(
        self,
        connection_name: str,
        username: str,
        password: str,
        client: str | None = None,
        max_sessions: int = MAX_SESSIONS,
        language: str = "EN",
        executable_path: str = r"C:\Program Files\SAP\FrontEnd\SAPGUI\saplogon.exe",
        window_title_re: str = "SAP Logon 800",
    ):
        self.connection_name = connection_name
        self.username = username
        self.password = password
        self.client = client
        self.language = language
        self.executable_path = executable_path
        self.window_title_re = window_title_re
        self.max_sessions = max_sessions

        self._sap_gui_auto = None
        self._app = None
        self._com_connection = None

    def _init_com(self):
        pythoncom.CoInitialize()

    def _uninit_com(self):
        pythoncom.CoUninitialize()

    def open_connection(self) -> GuiSession:
        # Check if connection already exists with same username.
        # If not found, create new connection, login and return
        # Use lock to ensure only one worker can call open_connection at a time
        lock_manager = get_global_lock_manager()
        with lock_manager:
            self._init_com()
            self._connect_to_engine()
            if not self._app:
                raise SAPConnectionError("Scripting engine not available")

            existing = self.is_connection_open()
            if existing:
                logger.info(f"Found existing connection for user: {self.username}")
                session_count = existing.Children.Count
                if session_count == 0:
                    # This ideally should never be possible since connection is already open
                    # In this case, assuming the connection is corrupt and we need to close this connection and establish a new one.
                    existing.CloseConnection()
                    return self.create_new_connection()
                # Create new session and return the session
                return self._create_new_session(existing)

            return self.create_new_connection()

    def create_new_connection(self) -> GuiSession:
        logger.info(f"No existing connection found for user: {self.username}")
        logger.info(f"Creating new connection for user: {self.username}")
        connection = self._app.OpenConnection(self.connection_name, True)
        session = GuiSession(connection.Children(0))
        self._login(session)
        return session

    def _create_new_session(self, connection) -> GuiSession:
        session_count = connection.Children.Count
        if session_count >= self.max_sessions:
            raise SAPConnectionError("Max sessions reached")

        logger.info(f"Current session count: {session_count}")
        logger.debug(f"Creating new session for user: {self.username}")
        sess = connection.Children(0)
        sess.CreateSession()
        time.sleep(3)
        logger.debug(f"New session count: {connection.Children.Count}")
        new_session = connection.Children(connection.Children.Count - 1)
        return GuiSession(new_session)

    def is_connection_open(self):
        logger.info(f"Checking for existing connection for user: {self.username}")
        children_count = self._app.Children.Count
        if children_count == 0:
            return None

        for i in range(children_count):
            conn = self._app.Children(i)
            if (
                str(conn.Description).strip().lower()
                != str(self.connection_name).strip().lower()
            ):
                continue

            session_count = conn.Children.Count
            if session_count == 0:
                return conn

            for j in range(conn.Children.Count):
                session = conn.Children(j)
                if session.Info.User == self.username:
                    return conn

        return None

    # TODO: Implement automatic password change and update password in keyring.
    def _login(
        self,
        session: GuiSession,
        terminate_other_sessions: bool = True,
    ) -> bool:
        """Performs SAP login with the provided credentials. It handles multiple login attempts, incorrect password attempts, terminates other sessions logged in other computers.

        Parameters
        ----------
        terminate_other_sessions : bool, optional
            If true, terminates other sessions logged in other computers, by default True
        Returns
        -------
        bool
            True if login was successful or user already logged in

        Raises
        ------
        SAPLoginError
            If login fails
        """
        user_field = session.find_by_id(
            SAPLoginScreenElements.username,
            raise_error=False,
        )
        if not user_field:
            logger.info("Login screen not found. Assuming user is already logged in.")
            return True

        logger.info(f"Logging in as {self.username}...")
        user_field.text = self.username
        session.find_by_id(SAPLoginScreenElements.password).text = self.password
        session.press_enter()

        # Check for immediate login errors (e.g., invalid credentials)
        status = session.raise_for_status(
            message="Login failed",
            exception=SAPLoginError,
        )

        # Handle multi-logon
        if status.text and "already logged on" in status.text.lower():
            logger.info("Multi-logon detected.")
            if not terminate_other_sessions:
                raise SAPLoginError("User already logged on in some other session.")

            logger.info("Terminating other sessions...")
            try:
                rb = session.find_by_id(
                    ControlID.TERMINATE_OTHER_SESSIONS_RADIO, raise_error=False
                )
                if rb:
                    rb.select()

                session.press_enter(1)
            except Exception as e:
                logger.warning(
                    f"Could not find multi-logon terminate radio button, attempting default enter: {e}"
                )
                session.press_enter(1)

        # Dismiss any other popup dialogs that may appear
        session.dismiss_popups()
        return True

    def _connect_to_engine(self):
        try:
            self._sap_gui_auto = win32.GetObject("SAPGUI")
            self._app = self._sap_gui_auto.GetScriptingEngine
        except Exception:
            # SAP Logon not running
            launch_application(self.executable_path, self.window_title_re)
            self._sap_gui_auto = win32.GetObject("SAPGUI")
            self._app = self._sap_gui_auto.GetScriptingEngine
