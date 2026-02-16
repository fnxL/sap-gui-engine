import logging
import subprocess
from pathlib import Path

from pywinauto.application import Application

from .exceptions import SAPError

logger = logging.getLogger(__name__)


class SAPLauncher:
    """
    Manages the startup of the SAP Logon application.
    """

    def __init__(
        self,
        executable_path: str = r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe",
        window_title: str = "SAP Logon 770",
    ):
        """
        Parameters
        ----------
        executable_path : str, optional
            Full path to saplogon.exe, by default r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"
        window_title : str, optional
            Title of the SAP Logon window to wait for, by default "SAP Logon 770"
        """
        self._executable_path = Path(executable_path)
        self._window_title = window_title
        self._sap_logon = None
        self._sap_logon_process = None
        self._sap_logon_process_id = None

    def launch(self) -> bool:
        """
        Launches SAP Logon if it is not already running.

        Returns
        -------
        bool
            True if launched, False if already running.

        Raises
        ------
        FileNotFoundError
            If the executable path does not exist.
        """

        if not self._executable_path.exists():
            raise FileNotFoundError(
                f"SAP executable not found at {self._executable_path}"
            )

        if self._is_running("saplogon.exe"):
            logger.debug("SAP Logon is already running")
            return False

        logger.info(f"Launching SAP Logon from {self._executable_path}")

        try:
            app = Application().start(str(self._executable_path), timeout=60)
            # Wait for the window to be ready
            dlg = app.window(title=self._window_title)
            dlg.wait("ready", timeout=60)

            logger.info("SAP Logon launched and ready.")
            return True
        except Exception as e:
            logger.error(f"Failed to launch SAP Logon: {e}")
            raise SAPError(f"Failed to launch SAP Logon: {e}") from e

    def _is_running(self, process_name: str) -> bool:
        """
        Checks if a process with the given name is running.

        Parameters
        ----------
        process_name : str
            The name of the process to check.

        Returns
        -------
        bool
            True if the process is running, False otherwise.
        """
        try:
            # Using 'tasklist' command for windows
            output = subprocess.check_output("tasklist", errors="ignore")
            return process_name.lower() in output.lower()
        except subprocess.SubprocessError:
            return False
