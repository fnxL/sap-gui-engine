from dataclasses import dataclass


@dataclass
class LoginElements:
    """Configuration for SAP Login screen elements."""

    username: str = "wnd[0]/usr/txtRSYST-BNAME"
    password: str = "wnd[0]/usr/pwdRSYST-BCODE"
