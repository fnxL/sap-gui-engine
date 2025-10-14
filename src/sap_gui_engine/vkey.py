from enum import IntEnum


class VKey(IntEnum):
    """
    SAP Keyboard VKey enum.
    Usage example:
    ```python
    VKey.SAVE.value
    # Returns: 11

    Vkey.SAVE.combo()
    # Returns: "Ctrl+S"

    Vkey.from_combo("Ctrl+S")
    # Returns: VKey.SAVE
    ```
    """

    ENTER = 0
    F1 = 1
    F2 = 2
    F3 = 3
    F4 = 4
    F5 = 5
    F6 = 6
    F7 = 7
    F8 = 8
    F9 = 9
    F10 = 10
    SAVE = 11  # Ctrl+S
    F12 = 12
    SHIFT_F1 = 13
    SHIFT_F2 = 14
    SHIFT_F3 = 15
    SHIFT_F4 = 16
    SHIFT_F5 = 17
    SHIFT_F6 = 18
    SHIFT_F7 = 19
    SHIFT_F8 = 20
    SHIFT_F9 = 21
    SHIFT_CTRL_0 = 22
    SHIFT_F11 = 23
    SHIFT_F12 = 24
    CTRL_F1 = 25
    CTRL_F2 = 26
    CTRL_F3 = 27
    CTRL_F4 = 28
    CTRL_F5 = 29
    CTRL_F6 = 30
    CTRL_F7 = 31
    CTRL_F8 = 32
    CTRL_F9 = 33
    CTRL_F10 = 34
    CTRL_F11 = 35
    CTRL_F12 = 36
    CTRL_SHIFT_F1 = 37
    CTRL_SHIFT_F2 = 38
    CTRL_SHIFT_F3 = 39
    CTRL_SHIFT_F4 = 40
    CTRL_SHIFT_F5 = 41
    CTRL_SHIFT_F6 = 42
    CTRL_SHIFT_F7 = 43
    CTRL_SHIFT_F8 = 44
    CTRL_SHIFT_F9 = 45
    CTRL_SHIFT_F10 = 46
    CTRL_SHIFT_F11 = 47
    CTRL_SHIFT_F12 = 48
    FIND = 70  # Ctrl+E
    SEARCH = 71  # Ctrl+F
    COMMENT = 72  # Ctrl+/
    UNCOMMENT = 73  # Ctrl+\
    NEW_SESSION = 74  # Ctrl+N
    OPEN = 75  # Ctrl+O
    CUT = 76  # Ctrl+X
    COPY = 77  # Ctrl+C
    PASTE = 78  # Ctrl+V
    UNDO = 79  # Ctrl+Z
    CTRL_PAGE_UP = 80
    PAGE_UP = 81
    PAGE_DOWN = 82
    CTRL_PAGE_DOWN = 83
    GOTO = 84  # Ctrl+G
    REFRESH = 85  # Ctrl+R
    PRINT = 86  # Ctrl+P

    def combo(self) -> str:
        """Return the SAP keyboard combination string for this VKey."""
        return _SAP_VKEY_COMBO_MAP[self]

    @classmethod
    def from_combo(cls, combo_str: str) -> "VKey":
        """Return the SAPVKey enum member from a keyboard combination string."""
        combo_str = combo_str.strip()
        return _SAP_COMBO_TO_VKEY[combo_str]


# Mapping kept OUTSIDE the enum to avoid TypeError
_SAP_VKEY_COMBO_MAP = {
    VKey.ENTER: "Enter",
    VKey.F1: "F1",
    VKey.F2: "F2",
    VKey.F3: "F3",
    VKey.F4: "F4",
    VKey.F5: "F5",
    VKey.F6: "F6",
    VKey.F7: "F7",
    VKey.F8: "F8",
    VKey.F9: "F9",
    VKey.F10: "F10",
    VKey.SAVE: "Ctrl+S",
    VKey.F12: "F12",
    VKey.SHIFT_F1: "Shift+F1",
    VKey.SHIFT_F2: "Shift+F2",
    VKey.SHIFT_F3: "Shift+F3",
    VKey.SHIFT_F4: "Shift+F4",
    VKey.SHIFT_F5: "Shift+F5",
    VKey.SHIFT_F6: "Shift+F6",
    VKey.SHIFT_F7: "Shift+F7",
    VKey.SHIFT_F8: "Shift+F8",
    VKey.SHIFT_F9: "Shift+F9",
    VKey.SHIFT_CTRL_0: "Shift+Ctrl+0",
    VKey.SHIFT_F11: "Shift+F11",
    VKey.SHIFT_F12: "Shift+F12",
    VKey.CTRL_F1: "Ctrl+F1",
    VKey.CTRL_F2: "Ctrl+F2",
    VKey.CTRL_F3: "Ctrl+F3",
    VKey.CTRL_F4: "Ctrl+F4",
    VKey.CTRL_F5: "Ctrl+F5",
    VKey.CTRL_F6: "Ctrl+F6",
    VKey.CTRL_F7: "Ctrl+F7",
    VKey.CTRL_F8: "Ctrl+F8",
    VKey.CTRL_F9: "Ctrl+F9",
    VKey.CTRL_F10: "Ctrl+F10",
    VKey.CTRL_F11: "Ctrl+F11",
    VKey.CTRL_F12: "Ctrl+F12",
    VKey.CTRL_SHIFT_F1: "Ctrl+Shift+F1",
    VKey.CTRL_SHIFT_F2: "Ctrl+Shift+F2",
    VKey.CTRL_SHIFT_F3: "Ctrl+Shift+F3",
    VKey.CTRL_SHIFT_F4: "Ctrl+Shift+F4",
    VKey.CTRL_SHIFT_F5: "Ctrl+Shift+F5",
    VKey.CTRL_SHIFT_F6: "Ctrl+Shift+F6",
    VKey.CTRL_SHIFT_F7: "Ctrl+Shift+F7",
    VKey.CTRL_SHIFT_F8: "Ctrl+Shift+F8",
    VKey.CTRL_SHIFT_F9: "Ctrl+Shift+F9",
    VKey.CTRL_SHIFT_F10: "Ctrl+Shift+F10",
    VKey.CTRL_SHIFT_F11: "Ctrl+Shift+F11",
    VKey.CTRL_SHIFT_F12: "Ctrl+Shift+F12",
    VKey.FIND: "Ctrl+E",
    VKey.SEARCH: "Ctrl+F",
    VKey.COMMENT: "Ctrl+/",
    VKey.UNCOMMENT: "Ctrl+\\",
    VKey.NEW_SESSION: "Ctrl+N",
    VKey.OPEN: "Ctrl+O",
    VKey.CUT: "Ctrl+X",
    VKey.COPY: "Ctrl+C",
    VKey.PASTE: "Ctrl+V",
    VKey.UNDO: "Ctrl+Z",
    VKey.CTRL_PAGE_UP: "Ctrl+PageUp",
    VKey.PAGE_UP: "PageUp",
    VKey.PAGE_DOWN: "PageDown",
    VKey.CTRL_PAGE_DOWN: "Ctrl+PageDown",
    VKey.GOTO: "Ctrl+G",
    VKey.REFRESH: "Ctrl+R",
    VKey.PRINT: "Ctrl+P",
}

# Reverse lookup map
_SAP_COMBO_TO_VKEY = {v: k for k, v in _SAP_VKEY_COMBO_MAP.items()}
