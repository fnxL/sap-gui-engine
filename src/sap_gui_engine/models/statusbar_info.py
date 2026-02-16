from typing import TypedDict


class StatusbarInfo(TypedDict):
    """Structure for SAP Status Bar information."""

    id: str
    text: str | None
    type: str
    number: str | None
    is_popup: bool
    parameter: str
