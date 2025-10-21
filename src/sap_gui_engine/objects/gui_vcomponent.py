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
        self.element = element

        # Set attributes only if they exist on the element
        if hasattr(element, 'AccLabelCollection'):
            self.acc_label_collection = element.AccLabelCollection
        if hasattr(element, 'AccText'):
            self.acc_text = element.AccText
        if hasattr(element, 'AccTextOnRequest'):
            self.acc_text_on_request = element.AccTextOnRequest
        if hasattr(element, 'AccTooltip'):
            self.acc_tooltip = element.AccTooltip
        if hasattr(element, 'Changeable'):
            self.changeable = element.Changeable
        if hasattr(element, 'DefaultTooltip'):
            self.default_tooltip = element.DefaultTooltip
        if hasattr(element, 'Height'):
            self.height = element.Height
        if hasattr(element, 'IconName'):
            self.icon_name = element.IconName
        if hasattr(element, 'IsSymbolFont'):
            self.is_symbol_font = element.IsSymbolFont
        if hasattr(element, 'Left'):
            self.left = element.Left
        if hasattr(element, 'Modified'):
            self.modified = element.Modified
        if hasattr(element, 'ParentFrame'):
            self.parent_frame = element.ParentFrame
        if hasattr(element, 'ScreenLeft'):
            self.screen_left = element.ScreenLeft
        if hasattr(element, 'ScreenTop'):
            self.screen_top = element.ScreenTop
        if hasattr(element, 'Tooltip'):
            self.tooltip = element.Tooltip
        if hasattr(element, 'Top'):
            self.top = element.Top
        if hasattr(element, 'Width'):
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
