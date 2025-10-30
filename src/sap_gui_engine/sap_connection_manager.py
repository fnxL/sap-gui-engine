import win32com.client as win32
import logging

logger = logging.getLogger(__name__)


class SAPConnectionManager:
    """Manages SAP connection lifecycle and state."""

    def __init__(self):
        self._app = None
        self._connection = None
        self._session = None

    @property
    def session(self):
        """Get the current SAP session."""
        return self._session

    def _connect_to_engine(self) -> None:
        """Connects to the SAPGUI Scripting Engine."""
        logger.debug("Connecting to SAPGUI Scripting Engine.")
        try:
            sap_gui = win32.GetObject("SAPGUI")
            self._app = sap_gui.GetScriptingEngine
            logger.info("Connected to SAPGUI Scripting Engine.")
        except Exception as e:
            logger.error(f"Error connecting to SAPGUI Object: {e}")
            raise Exception("SAP Logon is not running.")

    def open_connection(self, connection_name: str) -> bool:
        """Tries to connect to existing open connection, if not found then opens new one."""
        if not self._app:
            self._connect_to_engine()

        logger.debug("Trying to open existing connection if any.")
        try:
            self._connection = self._app.Children(0)
            if str(self._connection.Description).lower() == connection_name.lower():
                self._session = self._connection.Children(0)
                logger.info(f"Found existing open connection: {connection_name}")
                return True

        except Exception as e:
            print(e)
            logger.info(
                f"No existing connection found, opening new connection: {connection_name}"
            )

        # Open New Connection Here
        try:
            self._connection = self._app.OpenConnection(connection_name, True)
        except Exception as e:
            logger.error(f"Error opening connection: {e}")
            if "'sapgui component' could not be instantiated" in str(e).lower():
                logger.error("Please check your internet connection.")
                raise RuntimeError("Please check your internet connection.")

            raise ValueError("Please check your connection name.")

        self._session = self._connection.Children(0)
        logger.info("Attached to connection session successfully.")
        return True

    def close_connection(self) -> None:
        """Closes the current SAP session the script is connected to, but does not close other sessions."""
        if self._session:
            self._session = None
        if self._connection:
            self._connection.CloseSession("ses[0]")
            self._connection = None
        self._app = None
        logger.info("Connection closed successfully.")

    @property
    def is_connected(self) -> bool:
        """Check if currently connected to SAP."""
        return self._session is not None and self._connection is not None
