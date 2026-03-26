from dataclasses import dataclass


@dataclass
class StatusbarMsg:
    id: str
    type: str
    text: str | None
    number: str | None
    has_longtext: str | None
    is_popup: bool | None
    parameter: str | None
