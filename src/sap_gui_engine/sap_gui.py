import subprocess
import win32com.client as win32
import logging
from pathlib import Path
from pywinauto.application import Application
from sap_gui_engine.vkey import VKey
from sap_gui_engine.sap_element import SAPElement
from sap_gui_engine.mappings.login import DEFAULT_LOGIN_ELEMENTS, LoginScreenElements
from sap_gui_engine.exceptions import LoginError

logger = logging.getLogger(__name__)


class SAPGuiEngine:
    def __init__(
        self,
        connection_name: str,
        window_title: str,
        executable_path: str,
    ):
        self.connection_name = connection_name
        self.window_title = window_title
        self.executable_path = Path(executable_path)

        self.app = None
        self.connection = None
        self.session = None

        # Init
        self.launch_sap()
        self.open_connection(self.connection_name)
        self.maximize()

    def launch_sap(self):
        """Launches SAP Logon if not already running."""
        logger.debug("Launching SAP Logon if not already running.")
        if not self.executable_path.exists():
            logger.error(f"SAP executable not found at {self.executable_path}")
            raise FileNotFoundError(
                f"SAP executable not found at {self.executable_path}"
            )

        if "saplogon.exe" in str(subprocess.check_output("tasklist")):
            logger.debug("SAP Logon is already running")
            return False

        app = Application().start(str(self.executable_path), timeout=60)
        dlg = app.window(title=self.window_title)
        dlg.wait("ready", timeout=60)
        logger.info("SAP Logon is running")
        return True

    def _connect_to_engine(self):
        logger.debug("Connecting to SAPGUI Scripting Engine.")
        try:
            sap_gui = win32.GetObject("SAPGUI")
            self.app = sap_gui.GetScriptingEngine
            logger.info("Connected to SAPGUI Scripting Engine.")
        except Exception as e:
            logger.error(f"Error connecting to SAPGUI Object: {e}")
            raise Exception("SAP Logon is not running.")

    def open_connection(self, connection_name: str):
        """Tries to connect to existing open connection, if not found then opens new one."""
        if not self.app:
            self._connect_to_engine()

        logger.debug("Trying to open existing connection if any.")
        try:
            self.connection = self.app.Children(0)
            if str(self.connection.Description).lower() == connection_name.lower():
                self.session = self.connection.Children(0)
                logger.info(f"Found existing open connection: {connection_name}")
                return True

        except Exception:
            logger.info(
                f"No existing connection found, opening new connection: {connection_name}"
            )

        # Open New Connection Here
        try:
            self.connection = self.app.OpenConnection(connection_name, True)
        except Exception as e:
            logger.error(f"Error opening connection: {e}")
            raise ValueError(
                f"Cannot open connection {connection_name}. Please check connection name"
            )

        self.session = self.connection.Children(0)
        logger.info("Attached to connection session successfully.")
        return True

    def findById(self, id: str):
        try:
            return SAPElement(self.session.findById(id))
        except Exception as e:
            logger.error(f"Error getting element {id}: {e}")
            raise RuntimeError(f"Error getting element {id}")

    def maximize(self, window: int = 0):
        try:
            self.session.findById(f"wnd[{window}]").maximize()
        except Exception as e:
            logger.error(f"Error maximizing window {window}: {e}")
            raise RuntimeError(f"Error maximizing window: {window}")

    def sendVKey(self, key: VKey, window: int = 0, times: int = 1):
        """Sends a virtual key to a window"""
        try:
            for _ in range(times):
                self.session.findById(f"wnd[{window}]").sendVKey(key.value)

            return True
        except Exception as e:
            logger.error(f"Error sending vkey {key} to window {window}: {e}")
            raise RuntimeError(f"Error sending vkey {key} to window {window}")

    def get_status_info(self):
        try:
            status_bar = self.session.findById("wnd[0]/sbar")
            return {
                "id": status_bar.MessageId,
                "text": status_bar.text,
                "type": status_bar.MessageType,
                "number": status_bar.MessageNumber,
                "is_popup": status_bar.MessageAsPopup,
                "parameter": status_bar.MessageParameter,
            }
        except Exception as e:
            logger.error(f"Error getting status bar information: {e}")
            return None

    def login(
        self,
        username: str,
        password: str,
        terminate_other_sessions: bool = True,
        login_screen_elements: LoginScreenElements = DEFAULT_LOGIN_ELEMENTS,
    ):
        self.findById(login_screen_elements.username).set_value(username)
        self.findById(login_screen_elements.password).set_value(password)
        self.sendVKey(VKey.ENTER)

        status = self.get_status_info()
        if status["type"] == "E":
            logger.error(f"Login failed with status: {status}")
            logger.error(status["text"])
            raise LoginError(status["text"])

        logger.info("User login successful")
        if "already logged on" in status["text"].lower():
            logger.info(status["text"])
            if not terminate_other_sessions:
                raise LoginError(status["text"])

            logger.info("Terminating other sessions")
            self.session.findById("wnd[1]/usr/radMULTI_LOGON_OPT1").select()
            self.sendVKey(VKey.ENTER, window=1)

        # Check for number of attempts dialog, and press enter
        try:
            if str(self.findById("wnd[1]").text).lower() == "information":
                self.sendVKey(VKey.ENTER, window=1)
        except Exception as e:
            # The popup dialog did not appear, so we can continue
            pass

        return True
