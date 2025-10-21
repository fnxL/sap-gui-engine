from typing import Any


class GuiComponent:
    """
    Represents a GUI component in the SAP GUI system.

    This class wraps a COM object element and provides access to its properties
    such as container type, ID, name, parent, type, and type as number.
    """

    def __init__(self, element: Any):
        """
        Initialize the GuiComponent with a COM object element.

        Args:
            element: The COM object representing the SAP GUI element
        """
        # Set attributes only if they exist on the element
        if hasattr(element, 'ContainerType'):
            self.container_type = element.ContainerType
        if hasattr(element, 'id'):
            self.id = element.id
        if hasattr(element, 'name'):
            self.name = element.name
        if hasattr(element, 'parent'):
            self.parent = element.parent # The parent COM object
        if hasattr(element, 'type'):
            self.type = element.type
        if hasattr(element, 'TypeAsNumber'):
            self.type_as_number = element.TypeAsNumber
