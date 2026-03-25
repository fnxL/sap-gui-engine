from enum import StrEnum


class ControlID(StrEnum):
    MAIN_WINDOW = "wnd[0]"
    POPUP_WINDOW = "wnd[1]"
    STATUS_BAR = "wnd[0]/sbar"
    TERMINATE_OTHER_SESSIONS_RADIO = "wnd[1]/usr/radMULTI_LOGON_OPT1"
