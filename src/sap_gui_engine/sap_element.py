import logging
from typing import Any
from sap_gui_engine.exceptions import ComboBoxOptionNotFoundError

logger = logging.getLogger(__name__)


class SAPElement:
    """
    A wrapper class for SAP GUI elements that provides a consistent interface
    for interacting with different types of SAP controls.

    This class abstracts the underlying SAP GUI element and provides methods
    to perform common operations like setting values and clicking elements.
    """

    def __init__(self, element: Any) -> None:
        """
        Initialize the SAPElement wrapper.

        Args:
            element: The underlying SAP GUI element object
        """
        self._element = element
        self._name = element.name
        self._type = element.type
        self._text = str(element.text).strip()
        self._changeable = element.changeable
        if self._type == "GuiComboBox":
            self._key = element.key

    @property
    def element(self) -> Any:
        """Get the underlying SAP GUI element."""
        return self._element

    @property
    def name(self) -> str:
        """Get the name of the SAP element."""
        return self._name

    @property
    def type(self) -> str:
        """Get the type of the SAP element."""
        return self._type

    @property
    def text(self) -> str:
        """Get the text value of the SAP element."""
        return self._text

    @property
    def changeable(self) -> bool:
        """Get whether the SAP element is changeable."""
        return self._changeable

    def get_text(self) -> str:
        """
        Get the current value/text of the SAP element.

        Returns:
            str: The text value of the element
        """
        return str(self._text)

    def set_text(self, text: str) -> bool:
        """
        Sets or selects a text value for supported SAP element types.

        This method will only operate on changeable elements. For non-changeable elements, it logs an info message and returns False.

        Supported element types:
        - GuiTextField: Sets the text property
        - GUICTextField: Sets the text property
        - GuiComboBox: Selects an item from the combobox by value

        Args:
            value (str): The value to set or select

        Returns:
            bool: True if the value was successfully set, False otherwise

        Raises:
            ComboBoxOptionNotFoundError: If the specified item is not found in a combobox
            ValueError: If there's an error setting the value for a text field
        """
        if not self._changeable:
            logger.info(f"Element {self._element.name} is not changeable")
            return False

        if self._type == "GuiComboBox":
            return self._select_from_combobox(text)

        match self._type:
            case "GuiTextField" | "GuiCTextField" | "GuiPasswordField":
                try:
                    self._element.text = text
                    # Update internal text value after setting
                    self._text = str(self._element.text).strip()
                    return True
                except Exception as e:
                    logger.error(
                        f"Error setting text for element {self._element.name}: {e}"
                    )
                    raise ValueError(
                        f"Error setting text for element {self._element.name}"
                    ) from e
            case _:
                # For any other element type that is not supported for text setting
                logger.warning(
                    f"Setting text is not supported for element type: {self._type}"
                )
                return False

    def _select_from_combobox(self, text: str) -> bool:
        """
        Selects an option in a GuiComboBox element by matching its text.

        Args:
            item (str): The value of the item to select

        Returns:
            bool: True if the item was successfully selected

        Raises:
            ComboBoxOptionNotFoundError: If the specified item is not found in the combobox
        """
        key = None
        for entry in self._element.entries:
            if entry.value.lower() == text.lower():
                key = entry.key
                break

        if not key:
            raise ComboBoxOptionNotFoundError(f"Option: {text} not found in combobox")

        self._element.key = key
        # TODO: Find a way to update/refresh the element's state.

        return True

    def click(self) -> bool:
        """
        Clicks, presses, or selects the SAP element based on its type.

        This method performs the appropriate action for the following element types:
        - GuiButton: Presses the button
        - GuiTab: Selects the tab
        - GuiRadioButton: Selects the radio button
        - GuiCheckBox: Calling this method will toggle the checkbox

        Returns:
            bool: True after successfully performing the click action
        """
        try:
            match self._type:
                case "GuiButton":
                    self._element.press()
                case "GuiTab":
                    self._element.select()
                case "GuiRadioButton":
                    self._element.select()
                case "GuiCheckBox":
                    self._element.selected = not self._element.selected
        except Exception as e:
            logger.error(f"Error clicking element {self._element.name}: {e}")
            raise RuntimeError(f"Error clicking element {self._element.name}") from e

        return True
