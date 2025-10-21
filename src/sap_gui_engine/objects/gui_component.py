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
        self._container_type = element.ContainerType
        self._id = element.id
        self._name = element.name
        self._parent = element.parent
        self._type = element.type
        self._type_as_number = element.TypeAsNumber

    @property
    def container_type(self) -> str:
        """
        Get the container type of the GUI component.

        Returns:
            The container type of the element
        """
        return self._container_type

    @property
    def id(self) -> str:
        """
        Get the ID of the GUI component.

        Returns:
            The ID of the element
        """
        return self._id

    @property
    def name(self) -> str:
        """
        Get the name of the GUI component.

        Returns:
            The name of the element
        """
        return self._name

    @property
    def parent(self) -> Any:
        """
        Get the parent COM object of the GUI component.

        Returns:
            The parent object of the element
        """
        return self._parent

    @property
    def type(self) -> str:
        """
        Get the type of the GUI component.

        Returns:
            The type of the element
        """
        return self._type

    @property
    def type_as_number(self) -> int:
        """
        Get the type of the GUI component as a number.

        Returns:
            The type of the element as a number
        """
        return self._type_as_number
