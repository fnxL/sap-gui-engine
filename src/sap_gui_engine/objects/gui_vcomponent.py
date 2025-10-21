import logging
from typing import Any
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
        self._element = element # The COM object itself
        self.acc_label_collection = element.AccLabelCollection
        self.acc_text = element.AccText
        self.acc_text_on_request = element.AccTextOnRequest
        self.acc_tooltip = element.AccTooltip
        self.changeable = element.Changeable
        self.default_tooltip = element.DefaultTooltip
        self.height = element.Height
        self.icon_name = element.IconName
        self.is_symbol_font = element.IsSymbolFont
        self.left = element.Left
        self.modified = element.Modified
        self.parent_frame = element.ParentFrame
        self.screen_left = element.ScreenLeft
        self.screen_top = element.ScreenTop
        self.tooltip = element.Tooltip
        self.top = element.Top
        self.width = element.Width

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

    # Properties as direct attributes (previously using @property)
    # acc_label_collection: Returns the collection of GuiLabel objects assigned to this control in the ABAP Screen Painter.
    # acc_text: Returns an additional text for accessibility support.
    # acc_text_on_request: Returns an additional text for accessibility support that is shown on request.
    # acc_tooltip: Returns an additional tooltip text for accessibility support.
    # changeable: Returns whether the object is changeable (not disabled or read-only).
    # default_tooltip: Returns the tooltip text generated from the short text defined in the data dictionary for the given screen element type.
    # height: Returns the height of the component in pixels.
    # icon_name: Returns the name of the icon assigned to the object, or empty string if none assigned.
    # is_symbol_font: Returns whether the component's text is visualized in the SAP symbol font.
    # left: Returns the left position of the element in screen coordinates.
    # modified: Returns whether the object is modified (state changed by user but not sent to SAP system).
    # parent_frame: Returns the parent frame if the control is hosted by a Frame object, otherwise None.
    # screen_left: Returns the y position of the component in screen coordinates.
    # screen_top: Returns the x position of the component in screen coordinates.
    # tooltip: Returns the tooltip text designed to help a user understand the meaning of a given text field or button.
    # top: Returns the top coordinate of the element in screen coordinates.
    # width: Returns the width of the component in pixels.
