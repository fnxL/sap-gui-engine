from dataclasses import dataclass


@dataclass
class LoginScreenElements:
    """
    Represents the SAP GUI login screen element mappings.
    Attributes:
        username: SAP GUI element path for username field
        password: SAP GUI element path for password field
    """

    username: str
    password: str

    def __post_init__(self):
        """Validate that all required fields are non-empty strings in SAP GUI element format."""
        if not self.username or not isinstance(self.username, str):
            raise ValueError("Username element path must be a non-empty string")
        if not self.password or not isinstance(self.password, str):
            raise ValueError("Password element path must be a non-empty string")

        # Basic validation for SAP GUI element path format (should contain window reference)
        if not self.username.startswith("wnd["):
            raise ValueError(
                f"Username element path '{self.username}' should start with 'wnd['"
            )
        if not self.password.startswith("wnd["):
            raise ValueError(
                f"Password element path '{self.password}' should start with 'wnd['"
            )


DEFAULT_LOGIN_ELEMENTS = LoginScreenElements(
    username="wnd[0]/usr/txtRSYST-BNAME",
    password="wnd[0]/usr/pwdRSYST-BCODE",
)
