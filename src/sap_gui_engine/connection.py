import logging
from typing import Any

import win32com.client as win32

from .exceptions import SAPError

logger = logging.getLogger(__name__)


class SAPConnectionManager:
    """
    Manages the COM connection to the SAP GUI Scripting ENgine.
    """

    def __init__(self):
        self._app: Any = None
        self._connection = None
        self._session: Any = None

    @property
    def session(self) -> Any:
        if not self._session:
            raise SAPError("No active SAP session. Connect first.")

        return self._session

    def open_connection(self, connection_name: str) -> None:
        """
        Connects to an existing SAP connection or opens a new one.

        Parameters
        ----------
        connection_name : str
            The name of the connection entry in SAP Logon
        """
        if not self._app:
            self._connect_to_engine()

        if self._find_existing_connection(connection_name):
            return

        self._open_new_connection(connection_name)

    def close_session(self):
        """
        Closes the current SAP session the script is attached to. This does not close the other sesssions.
        """
        if self._session:
            session_id = self._session.id

        if self._connection:
            try:
                self._connection.CloseSession(session_id)
                self._connection = None
            except Exception as e:
                raise SAPError(f"Error closing session: {e}") from e

        self._app = None
        logger.info("SAP session closed successfully")

    def close_connection(self):
        """
        Closes the connection including all the sessions.
        """
        if self._connection:
            try:
                self._connection.CloseConnection()
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
            finally:
                self._connection = None
                self._session = None
                logger.info("SAP connection closed.")

    def _connect_to_engine(self):
        """
        Connects to the SAPGUI Scripting Engine COM object.
        """
        try:
            sap_gui = win32.GetObject("SAPGUI")
            self._app = sap_gui.GetScriptingEngine
            logger.debug("Connected to SAPGUI Scripting Engine.")
        except Exception as e:
            logger.error("Failed to get SAPGUI Scripting Engine. Is SAP Logon running?")
            raise SAPError(
                "Could not connect to SAPGUI Scripting Engine. Please check if SAP Logon is running."
            ) from e

    def _find_existing_connection(self, connection_name: str) -> bool:
        """Iterates through open connections to find a match.
        Returns
        -------
        bool
            True if a match is found, False otherwise.
        """
        children_count = self._app.Children.Count
        if children_count == 0:
            logger.warning("No open connections found.")
            return False

        try:
            for i in range(children_count):
                conn = self._app.Children(i)
                if (
                    str(conn.Description).strip().lower()
                    == connection_name.strip().lower()
                ):
                    logger.info(f"Attaching to existing connection: {connection_name}")
                    self._connection = conn
                    self._session = conn.Children(0)
                    return True

        except Exception as e:
            logger.warning("No existing connection found.")

        return False

    def _open_new_connection(self, connection_name: str) -> None:
        """
        Opens a new connection
        """
        logger.info(f"Opening new connection: {connection_name}")

        try:
            # OpenConnection(Name, Sync)
            self._connection = self._app.OpenConnection(connection_name, True)
            self._session = self._connection.Children(0)
        except Exception as e:
            logger.error(f"Failed to open connection '{connection_name}': {str(e)}")

            if "'sapgui component' could not be instantiated" in str(e).lower():
                raise SAPError("Please check your internet connection/VPN.") from e

            raise SAPError(
                f"Could not open connection '{connection_name}'. Please check your connection name and if SAP Logon is running."
            ) from e
