import logging
from pathlib import Path
from .sap_launcher import SAPLauncher
from .sap_connection_manager import SAPConnectionManager
from .mappings import LoginScreenElements, DEFAULT_LOGIN_ELEMENTS, VKey
from .exceptions import LoginError

logger = logging.getLogger(__name__)


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

    def login(
        self,
        username: str,
        password: str,
        terminate_other_sessions: bool = True,
        login_screen_elements: LoginScreenElements = DEFAULT_LOGIN_ELEMENTS,
    ) -> bool:
        """Performs SAP login with provided credentials only if it finds login elements, with all possible exceptions/scenarios handled."""
        try:
            self.session.findById(login_screen_elements.username).text = username
            self.session.findById(login_screen_elements.password).text = password
            self.session.sendVKey(VKey.ENTER)
        except Exception as e:
            logger.warning(
                f"Either user is already logged on or login screen is currently not open: {str(e)}",
            )
            return True

        status = self.session.get_status_info()
        if status and status["type"] == "E":
            logger.error(f"Login failed with status: {status}")
            raise LoginError(status["text"])

        logger.info("User login successful")

        # Check if user is already logged on in some other instance
        if status and "already logged on" in status["text"].lower():
            logger.info(status["text"])
            if not terminate_other_sessions:
                raise LoginError(status["text"])

            logger.info("Terminating other sessions")
            self.session.findById("wnd[1]/usr/radMULTI_LOGON_OPT1").select()
            self.session.sendVKey(VKey.ENTER, window=1)

        self.session.dismiss_popups_until_none()
        return True
