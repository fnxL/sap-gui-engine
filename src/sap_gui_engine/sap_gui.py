from pathlib import Path
from pywinauto.application import Application
import subprocess
import win32com.client as win32
from sap_gui_engine.vkey import VKey
from sap_gui_engine.mappings.login import DEFAULT_LOGIN_ELEMENTS, LoginScreenElements


class SAPGuiEngine:
    def __init__(self, connection_name: str, window_title: str, executable_path: str):
        self.connection_name = connection_name
        self.window_title = window_title
        self.executable_path = Path(executable_path)

        self.app = None
        self.connection = None
        self.session = None

        self.launch_sap()
        self.open_connection(self.connection_name)
        self.session.findById()

    def launch_sap(self):
        """Launches SAP Logon if not already running."""
        if not self.executable_path.exists():
            raise FileNotFoundError(
                f"SAP executable not found at {self.executable_path}"
            )

        if "saplogon.exe" in str(subprocess.check_output("tasklist")):
            return False

        app = Application().start(str(self.executable_path), timeout=60)
        dlg = app.window(title=self.window_title)
        dlg.wait("ready", timeout=60)
        return True

    def _connect_to_engine(self):
        try:
            sap_gui = win32.GetObject("SAPGUI")
            self.app = sap_gui.GetScriptingEngine
        except Exception as e:
            print(f"Error connecting to SAP GUI: {e}")
            raise Exception("SAP Logon is not running.")

    def open_connection(self, connection_name: str):
        """Tries to connect to existing open connection, if not found then opens new one."""
        if not self.app:
            self._connect_to_engine()

        try:
            self.connection = self.sap_app.Children(0)
            if str(self.connection.Description).lower() == connection_name.lower():
                self.session = self.connection.Children(0)
                print("Existing open connection found")
                return True

            raise ValueError(f"SAP Connection {self.connection_name} not found")
        except Exception as e:
            # This would mean that the connection is not open, so open new one.
            print(f"Existing connection not found, opening new one: {e}")

        try:
            self.connection = self.sap_app.OpenConnection(connection_name, True)
        except Exception as e:
            print(f"Error opening connection: {e}")
            raise ValueError(
                f"Cannot open connection {connection_name}. Please check connection name"
            )

        self.session = self.connection.Children(0)
        return True

    def findById(self, id: str):
        try:
            return self.session.findById(id)
        except Exception as e:
            print(f"Error getting element {id}: {e}")
            raise RuntimeError(f"Error getting element {id}")

    def sendVKey(self, key: VKey, window: int = 0, times: int = 1):
        try:
            for _ in range(times):
                self.findById(f"wnd[{window}]").sendVKey(key.value)

            return True
        except Exception as e:
            print(f"Error sending vkey: {e}")
            raise RuntimeError(f"Error sending vkey: {key}")

    def login(
        self,
        username: str,
        password: str,
        login_screen_elements: LoginScreenElements = DEFAULT_LOGIN_ELEMENTS,
    ):
        pass
