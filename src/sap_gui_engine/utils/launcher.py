import logging
import subprocess
import sys
from pathlib import Path
from typing import Union

from pywinauto.application import Application

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 60


def is_process_running(process_name: str) -> bool:
    """
    Checks if a process with the given name is running.

    Note: Currently only supports Windows systems.

    Parameters
    ----------
    process_name : str
        Name of the process to check for

    Returns
    -------
    bool
        True if process is running, False otherwise
    """
    if sys.platform != "win32":
        raise NotImplementedError("is_process_running is only supported on Windows")

    try:
        output = subprocess.check_output(
            "tasklist", shell=True, text=True, stderr=subprocess.DEVNULL
        )
        return process_name.lower() in output.lower()
    except subprocess.CalledProcessError:
        # If tasklist command fails, assume process is not running
        return False


def launch_application(
    executable_path: Path | str,
    window_title_pattern: str,
    timeout: int = DEFAULT_TIMEOUT,
) -> bool:
    """
    Launches a Windows application and waits until a dialog with given window title appears/is ready.

    Parameters
    ----------
    executable_path : Union[Path, str]
        Path to the executable file to launch
    window_title_pattern : str
        Title pattern of the window to wait for after launching the application
    timeout : int, optional
        Maximum time to wait for the application to become ready (default is 60 seconds)

    Returns
    -------
    bool
        True if the application was successfully launched and is ready

    Raises
    ------
    FileNotFoundError
        If the executable file does not exist at the specified path
    NotImplementedError
        If called on a non-Windows platform
    """
    if sys.platform != "win32":
        raise NotImplementedError("Launch function is only supported on Windows")

    _executable_path = Path(executable_path)
    if not _executable_path.exists():
        raise FileNotFoundError(f"Executable not found at {_executable_path}")

    if is_process_running(_executable_path.name):
        logger.info(f"Process {_executable_path.name} is already running")
        return True

    try:
        logger.info(f"Starting application: {_executable_path}")
        app = Application().start(str(_executable_path), timeout=timeout)

        # Wait for the window to be ready
        logger.info(f"Waiting for window _rewith title: {window_title_pattern}")
        dlg = app.window(title_re=window_title_pattern)
        dlg.wait("ready", timeout=timeout)

        logger.info("Application launched and ready")
        return True

    except TimeoutError as te:
        error_msg = f"Timeout while waiting for application '{_executable_path.name}' to become ready: {te}"
        logger.error(error_msg)
        raise TimeoutError(error_msg) from te
    except Exception as e:
        error_msg = f"Failed to launch application {_executable_path.name}: {e}"
        logger.error(error_msg)
        return False
