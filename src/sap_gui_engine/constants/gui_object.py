from enum import StrEnum


class GuiObject(StrEnum):
    """
    A String Enum containing all SAP GUI Scripting Objects.
    The enum member names are in UPPER_SNAKE_CASE for Python convention,
    and their values are the original object names as used by the SAP Scripting API.

    Source: https://help.sap.com/docs/sap_gui_for_windows/b47d018c3b9b45e897fa
    f66a6c0885a8/a2e9357389334dc89eecc1fb13999ee3.html
    """

    APPLICATION = "GuiApplication"
    BAR_CHART = "GuiBarChart"
    BOX = "GuiBox"
    BUTTON = "GuiButton"
    CALENDAR = "GuiCalendar"
    CHART = "GuiChart"
    CHECKBOX = "GuiCheckBox"
    COLLECTION = "GuiCollection"
    COLOR_SELECTOR = "GuiColorSelector"
    COMBO_BOX = "GuiComboBox"
    COMBO_BOX_CONTROL = "GuiComboBoxControl"
    COMBO_BOX_ENTRY = "GuiComboBoxEntry"
    CONNECTION = "GuiConnection"
    CONTAINER = "GuiContainer"
    CTEXT_FIELD = "GuiCTextField"
    CONTAINER_SHELL = "GuiContainerShell"
    FRAME_WINDOW = "GuiFrameWindow"
    GRID_VIEW = "GuiGridView"
    LABEL = "GuiLabel"
    MAIN_WINDOW = "GuiMainWindow"
    MENU = "GuiMenu"
    MENUBAR = "GuiMenubar"
    MESSAGE_WINDOW = "GuiMessageWindow"
    MODAL_WINDOW = "GuiModalWindow"
    PASSWORD_FIELD = "GuiPasswordField"
    PICTURE = "GuiPicture"
    RADIO_BUTTON = "GuiRadioButton"
    SCROLLBAR = "GuiScrollbar"
    SESSION = "GuiSession"
    SESSION_INFO = "GuiSessionInfo"
    STATUS_BAR = "GuiStatusbar"
    TAB = "GuiTab"
    TABLE_CONTROL = "GuiTableControl"
    TABLE_COLUMN = "GuiTableColumn"
    TABLE_ROW = "GuiTableRow"
    TAB_STRIP = "GuiTabStrip"
    TEXT_FIELD = "GuiTextField"
    TITLE_BAR = "GuiTitlebar"
    TOOL_BAR = "GuiToolbar"
    TREE = "GuiTree"
    VCOMPONENT = "GuiVComponent"
