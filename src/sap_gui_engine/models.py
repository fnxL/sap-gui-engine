from dataclasses import dataclass
from typing import TypedDict


@dataclass
class LoginElements:
    """Configuration for SAP Login screen elements."""

    username: str = "wnd[0]/usr/txtRSYST-BNAME"
    password: str = "wnd[0]/usr/pwdRSYST-BCODE"


class StatusbarInfo(TypedDict):
    """Structure for SAP Status Bar information."""

    id: str
    text: str | None
    type: str
    number: str | None
    is_popup: bool
    parameter: str
