import logging
from dataclasses import dataclass

import win32com.client as win32

from sap_gui_engine.constants import ControlID
from sap_gui_engine.exceptions import SAPConnectionError, SAPLoginError
from sap_gui_engine.objects import GuiSession
from sap_gui_engine.utils import launch_application

logger = logging.getLogger(__name__)


@dataclass
class SAPLoginScreenElements:
    client: str = "wnd[0]/usr/txtRSYST-MANDT"
    username: str = "wnd[0]/usr/txtRSYST-BNAME"
    password: str = "wnd[0]/usr/pwdRSYST-BCODE"
    language: str = "wnd[0]/usr/txtRSYST-LANGU"


class SAPGuiEngine:
    def __init__(
        self,
        connection_name: str,
        username: str,
        password: str,
        client: str | None = None,
        terminate_other_sessions: bool = True,
        language: str | None = None,
        executable_path: str = r"C:\Program Files\SAP\FrontEnd\SAPGUI\saplogon.exe",
        window_title_re: str = "SAP Logon 800",
    ):
        """Initialize SAPGuiEngine with connection parameters.

        Parameters
        ----------
        connection_name : str
            Name of the SAP connection to connect to
        username : str
            Username for SAP login
        password : str
            Password for SAP login
        client : str | None, optional
            Client number for SAP login, by default None
        terminate_other_sessions : bool, optional
            Whether to terminate other sessions when multi-logon is detected, by default True
        language : str | None, optional
            Language code for SAP login, by default None
        executable_path : str, optional
            Path to SAP Logon executable, by default r"C:\\Program Files\\SAP\\FrontEnd\\SAPGUI\\saplogon.exe"
        window_title_re : str, optional
            Regular expression for SAP Logon window title, by default "SAP Logon 800"
        """
        self.connection_name = connection_name
        self.username = username
        self.password = password
        self.client = client
        self.terminate_other_sessions = terminate_other_sessions
        self.language = language
        self.executable_path = executable_path
        self.window_title_re = window_title_re

        self._sap_gui_auto = None
        self._app = None
        self._com_connection = None

    def open_connection(self) -> GuiSession:
        """Open a connection to the SAP system.

        This method tries to find existing open connections of the given user
        and attaches to the first session of the connection. If no open connection
        is found, it tries to open a new connection, perform login and returns
        the GuiSession object. It also launches the SAP Logon application if
        the application is not already running.

        Returns
        -------
        GuiSession
            The GuiSession object of the opened/existing connection to interact
            with the session.

        Raises
        ------
        SAPConnectionError
            If connection fails to open or login fails.
        SAPLoginError
            If login fails.
        TimeoutError
            If SAP Logon application fails to launch within timeout, default = 60 seconds.
        """

        # Launch SAP Logon application if not already running, and connect to scripting engine
        self._connect_to_engine()
        if not self._app:
            raise SAPConnectionError("Scripting engine not available")

        # Check if connection already exists with same username.
        # If not found, create new connection, login and return
        existing_connection = self._is_connection_open()
        if existing_connection:
            logger.info(f"Found existing connection for user: {self.username}")

            session_count = existing_connection.Children.Count

            if session_count == 0:
                # This is never possible since connection is already open
                # In this case, assuming the connection is corrupt and we need to close this connection and establish a new one.
                existing_connection.CloseConnection()
                return self._create_new_connection()

            # Connection is already open, so attach to the first session
            logger.info(f"Attaching to first session for user: {self.username}")
            session = GuiSession(existing_connection.Children(0))
            self._login(session)
            return session

        logger.info(f"No existing connection found for user: {self.username}")

        return self._create_new_connection()

    def close_connection(self):
        """Close the SAP connection including all sessions.

        This method closes the SAP connection and all associated sessions,
        and cleans up the internal references to the SAP GUI objects.
        """
        try:
            self._com_connection.CloseConnection()
            logger.info("SAP Connection closed.")
        except Exception as e:
            logger.error(f"Error while closing connection: {e}")
        finally:
            self._app = None
            self._sap_gui_auto = None

    def _is_connection_open(self):
        """Check if a connection for the specified user is already open.

        This method checks for existing open connections for the given user
        and returns the GuiConnection SAP COM object if found, otherwise None.

        Returns
        -------
        object or None
            The underlying native GuiConnection COM object if connection is open,
            otherwise None
        """
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
            # Session count is greater than 0, so check if any of the sessions are logged in as the given user
            for j in range(conn.Children.Count):
                session = conn.Children(j)
                if session.Info.User == self.username:
                    return conn

        return None

    def _create_new_connection(self) -> GuiSession:
        logger.info(f"Creating new connection for user: {self.username}")
        connection = self._app.OpenConnection(self.connection_name, True)
        session = GuiSession(connection.Children(0))
        self._login(session)
        return session

    def _login(
        self,
        session: GuiSession,
    ) -> bool:
        """Perform SAP login with provided credentials.

        This method performs SAP login with the provided credentials, handling
        multiple login attempts, incorrect password attempts, terminating other
        sessions logged in other computers, and dismissing any additional popups
        that may appear after login.

        Parameters
        ----------
        session : GuiSession
            The GuiSession object to perform login on

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

        if self.client:
            session.find_by_id(SAPLoginScreenElements.client).text = self.client

        if self.language:
            session.find_by_id(SAPLoginScreenElements.language).text = self.language

        session.press_enter()

        # Check for immediate login errors (e.g., invalid credentials)
        status = session.raise_for_status(
            message="Login Failed",
            exception=SAPLoginError,
        )

        # Handle multi-logon
        if status.text and "already logged on" in status.text.lower():
            logger.info("Multi-logon detected.")
            if not self.terminate_other_sessions:
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
        session.dismiss_popups(limit=10)
        return True

    def _connect_to_engine(self):
        """Establish connection to the SAP GUI scripting engine.

        This method establishes connection to the SAP GUI scripting engine
        by launching the SAP Logon application and connecting to the COM object.

        Raises
        ------
        SAPConnectionError
            If unable to connect to SAP GUI scripting engine after
            attempting to launch SAP Logon application
        TimeoutError
            If SAP logon failed to launch within the specified timeout period, default 60 seconds
        """
        launch_application(self.executable_path, self.window_title_re)

        try:
            self._sap_gui_auto = win32.GetObject("SAPGUI")
            self._app = self._sap_gui_auto.GetScriptingEngine
        except Exception as e:
            raise SAPConnectionError(
                f"Could not connect to SAP GUI scripting engine: {e}"
            ) from e
