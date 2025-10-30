from pathlib import Path
from .sap_launcher import SAPLauncher


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
