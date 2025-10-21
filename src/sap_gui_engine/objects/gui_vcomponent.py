import logging
from typing import Any
from sap_gui_engine.exceptions import ComboBoxOptionNotFoundError
from .gui_component import GuiComponent

logger = logging.getLogger(__name__)


class GuiVComponent(GuiComponent):
    """
    Represents a SAP GUI Visual Component (GuiVComponent).

    GuiVComponent extends the base GuiComponent and provides access to visual properties
    and methods available in SAP GUI components. This class provides access to various
    properties like accessibility text, tooltip information, position, dimensions, and
    other visual attributes of SAP GUI controls.

    Methods available in SAP GUI components include:
    - DumpState: Dumps the state of the object for debugging purposes
    - SetFocus: Sets the focus onto an object
    - Visualize: Displays a red frame around the specified component for visualization

    Properties include accessibility information, position coordinates, dimensions,
    changeability status, and other visual attributes as defined in the SAP GUI API.
    """

    def __init__(self, element: Any):
        super().__init__(element)
        self._element = element
        self._acc_label_collection = element.AccLabelCollection
        self._acctext = element.AccText
        self._acctext_on_request = element.AccTextOnRequest
        self._acc_tooltip = element.AccTooltip
        self._changeable = element.Changeable
        self._default_tooltip = element.DefaultTooltip
        self._height = element.Height
        self._icon_name = element.IconName
        self._is_symbol_font = element.IsSymbolFont
        self._left = element.Left
        self._modified = element.Modified
        self._parent_frame = element.ParentFrame
        self._screen_left = element.ScreenLeft
        self._screen_top = element.ScreenTop
        self._tooltip = element.Tooltip
        self._top = element.Top
        self._width = element.Width

    # Methods from SAP API
    def dump_state(self, inner_object: str = "") -> Any:
        """
        Dumps the state of the object for debugging purposes.

        Args:
            inner_object (str): Specifies for which internal object the data should be dumped.
                               Only complex components like GuiCtrlGridView support this parameter.
                               Use empty string to get general information about the control's state.

        Returns:
            GuiCollection: A hierarchy of collections containing the state information.
                          The return is three levels deep with OpCodes like GPR, MR, GP, M
                          to represent property access and method calls.

        Note:
            The result is a three-level collection structure where the top level contains
            entries for each property, the second level contains complete information for
            one property, and the third level contains OpCode, property/method name, and
            parameter values with return values where applicable.
        """
        return self._element.DumpState(inner_object)

    def set_focus(self) -> None:
        """
        Sets the focus onto this object in the SAP GUI.

        Note: Interacting with an object through scripting does not automatically change
        the focus. Some SAP applications explicitly check for focus and behave differently
        depending on the focused object.
        """
        self._element.SetFocus()

    def visualize(self, on: bool, inner_object: str | None) -> int:
        """
        Displays a red frame around the specified component for visualization.

        Args:
            on (bool): True to display the red frame, False to remove it
            inner_object (str, optional): For components that support inner objects (like cells
                                        in a grid view), specifies which inner object to frame

        Returns:
            int: Status code indicating the result of the operation

        Note: Some components such as GuiCtrlGridView support displaying the frame around
        inner objects such as cells. The format of the inner_object string is the same
        as for the dumpState method.
        """
        if inner_object is not None:
            return self._element.Visualize(on, inner_object)
        else:
            return self._element.Visualize(on)

    @property
    def acc_label_collection(self) -> Any:
        """
        Returns the collection of GuiLabel objects assigned to this control in the ABAP Screen Painter.

        Returns:
            GuiComponentCollection: Collection containing objects of type GuiLabel that were
                                   assigned to this control in the ABAP Screen Painter.
        """
        return self._acc_label_collection

    @property
    def acc_text(self) -> str:
        """
        Returns an additional text for accessibility support.

        Returns:
            str: Additional text for accessibility support
        """
        return self._acctext

    @property
    def acc_text_on_request(self) -> str:
        """
        Returns an additional text for accessibility support that is shown on request.

        Returns:
            str: Additional text for accessibility support shown on request
        """
        return self._acctext_on_request

    @property
    def acc_tooltip(self) -> str:
        """
        Returns an additional tooltip text for accessibility support.

        Returns:
            str: Additional tooltip text for accessibility support
        """
        return self._acc_tooltip

    @property
    def changeable(self) -> bool:
        """
        Returns whether the object is changeable (not disabled or read-only).

        Returns:
            bool: True if the object is changeable, False otherwise

        Note: An object is changeable if it is neither disabled nor read-only.
        """
        return self._changeable

    @property
    def default_tooltip(self) -> str:
        """
        Returns the tooltip text generated from the short text defined in the data dictionary
        for the given screen element type.

        Returns:
            str: Tooltip text generated from the data dictionary
        """
        return self._default_tooltip

    @property
    def height(self) -> int:
        """
        Returns the height of the component in pixels.

        Returns:
            int: Height of the component in pixels
        """
        return self._height

    @property
    def icon_name(self) -> str:
        """
        Returns the name of the icon assigned to the object, or empty string if none assigned.

        Returns:
            str: Name of the icon assigned to the object, or empty string if none
        """
        return self._icon_name

    @property
    def is_symbol_font(self) -> int:
        """
        Returns whether the component's text is visualized in the SAP symbol font.

        Returns:
            int: 1 if the component's text is in SAP symbol font, 0 otherwise

        Note: The property is TRUE if the component's text is visualized in the SAP symbol font.
        """
        return self._is_symbol_font

    @property
    def left(self) -> int:
        """
        Returns the left position of the element in screen coordinates.

        Returns:
            int: Left position of the element in screen coordinates
        """
        return self._left

    @property
    def modified(self) -> bool:
        """
        Returns whether the object is modified (state changed by user but not sent to SAP system).

        Returns:
            bool: True if the object is modified, False otherwise

        Note: An object is modified if its state has been changed by the user and this change
        has not yet been sent to the SAP system.
        """
        return self._modified

    @property
    def parent_frame(self) -> Any:
        """
        Returns the parent frame if the control is hosted by a Frame object, otherwise None.

        Returns:
            GuiComponent: The parent frame if the control is hosted by a Frame object, otherwise None

        Note: If the control is hosted by the Frame object, the value of the property is this frame.
        Otherwise NULL.
        """
        return self._parent_frame

    @property
    def screen_left(self) -> int:
        """
        Returns the y position of the component in screen coordinates.

        Returns:
            int: The y position of the component in screen coordinates
        """
        return self._screen_left

    @property
    def screen_top(self) -> int:
        """
        Returns the x position of the component in screen coordinates.

        Returns:
            int: The x position of the component in screen coordinates
        """
        return self._screen_top






    @property
    def tooltip(self) -> str:
        """
        Returns the tooltip text designed to help a user understand the meaning of a given
        text field or button.

        Returns:
            str: The tooltip text for the component

        Note: The tooltip contains a text which is designed to help a user understand the
        meaning of a given text field or button.
        """
        return self._tooltip

    @property
    def top(self) -> int:
        """
        Returns the top coordinate of the element in screen coordinates.

        Returns:
            int: Top coordinate of the element in screen coordinates
        """
        return self._top

    @property
    def width(self) -> int:
        """
        Returns the width of the component in pixels.

        Returns:
            int: Width of the component in pixels
        """
        return self._width
