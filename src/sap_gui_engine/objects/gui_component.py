from typing import Any


class GuiComponent:
    """
    Combines the properties of the GuiVComponent and GuiComponent classes.
    This class wraps a COM object element and provides access to its properties
    such as container type, ID, name, parent, type, and type as number.

    Methods available:
        - set_focus: Sets the focus onto this object in the SAP GUI.
        - visualize: Displays a red frame around the specified component for visualization.
    """

    def __init__(self, element: Any):
        """
        Initialize the GuiComponent with a COM object element.

        Args:
            element: The COM object representing the SAP GUI element
        """
        self.element = element
        # Set attributes only if they exist on the element
        if hasattr(element, "ContainerType"):
            self.container_type = element.ContainerType
        if hasattr(element, "id"):
            self.id = element.id
        if hasattr(element, "name"):
            self.name = element.name
        if hasattr(element, "parent"):
            self.parent = element.parent  # The parent COM object
        if hasattr(element, "type"):
            self.type = element.type
        if hasattr(element, "TypeAsNumber"):
            self.type_as_number = element.TypeAsNumber

        if hasattr(element, "Changeable"):
            self.changeable = element.Changeable
        if hasattr(element, "DefaultTooltip"):
            self.default_tooltip = element.DefaultTooltip
        if hasattr(element, "Tooltip"):
            self.tooltip = element.Tooltip
        if hasattr(element, "Top"):
            self.top = element.Top
        if hasattr(element, "Left"):
            self.left = element.Left
        if hasattr(element, "Width"):
            self.width = element.Width
        if hasattr(element, "Height"):
            self.height = element.Height
        if hasattr(element, "IconName"):
            self.icon_name = element.IconName
        if hasattr(element, "ScreenLeft"):
            self.screen_left = element.ScreenLeft
        if hasattr(element, "ScreenTop"):
            self.screen_top = element.ScreenTop

    def set_focus(self) -> None:
        """
        Sets the focus onto this object in the SAP GUI.
        """
        self.element.SetFocus()

    def visualize(self, on: bool, inner_object: str | None):
        """
        Displays a red frame around the specified component for visualization.

        Args:
            on (bool): True to display the red frame, False to remove it
        """
        if inner_object is not None:
            return self.element.Visualize(on, inner_object)
        else:
            return self.element.Visualize(on)
