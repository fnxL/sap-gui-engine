from pathlib import Path
from .sap_launcher import SAPLauncher
from .sap_connection_manager import SAPConnectionManager


class SAPGuiEngine:
    def __init__(
        self,
        connection_name: str,
        window_title: str = "SAP Logon 770",
        executable_path: str
        | Path = r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe",
    ):
        if isinstance(executable_path, str):
            executable_path = Path(executable_path)

        self._sap_launcher = SAPLauncher(executable_path, window_title)
        self._sap_launcher.launch_sap()
        self._connection_manager = SAPConnectionManager()
        self._connection_manager.open_connection(connection_name)

        @property
        def session(self):
            return self._connection_manager.session

        @property
        def connection_manager(self):
            """Get the connection manager to access it's methods and properties."""
            return self._connection_manager
