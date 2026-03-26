from dataclasses import dataclass


@dataclass
class StatusbarMsg:
    id: str
    type: str
    text: str
    number: str
    has_longtext: int
    is_popup: bool | None
