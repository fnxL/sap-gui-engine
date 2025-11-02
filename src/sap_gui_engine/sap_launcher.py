import subprocess
import logging
from pathlib import Path
from pywinauto.application import Application

logger = logging.getLogger(__name__)


class SAPLauncher:
    """Handles launching of SAP application."""

    def __init__(self, executable_path: Path, window_title: str):
        self._executable_path = executable_path
        self._window_title = window_title

    def launch_sap(self) -> bool:
        """Launches SAP Logon if not already running and waits for it to be ready."""

        logger.debug("Launching SAP Logon if not already running.")

        if not self._executable_path.exists():
            raise FileNotFoundError(
                f"SAP executable not found at {self._executable_path}"
            )

        if "saplogon.exe" in str(subprocess.check_output("tasklist")):
            logger.debug("SAP Logon is already running")
            return False

        app = Application().start(str(self._executable_path), timeout=60)
        dlg = app.window(title=self._window_title)
        dlg.wait("ready", timeout=60)
        logger.info("SAP Logon is running")
        return True
