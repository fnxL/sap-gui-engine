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
        self.container_type = element.ContainerType
        self.id = element.id
        self.name = element.name
        self.parent = element.parent # The parent COM object
        self.type = element.type
        self.type_as_number = element.TypeAsNumber
