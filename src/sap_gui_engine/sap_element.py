import logging
from typing import Any
from sap_gui_engine.exceptions import ComboBoxItemNotFoundError

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
        self.element = element
        self.name = element.name
        self.type = element.type
        self.text = element.text
        self.changeable = element.changeable

    def set_value(self, value: str) -> bool:
        """
        Sets or selects a value for supported SAP element types.

        This method will only operate on changeable elements. For non-changeable
        elements, it logs an info message and returns False.

        Supported element types:
        - GuiTextField: Sets the text property
        - GUICTextField: Sets the text property
        - GuiComboBox: Selects an item from the combobox by value

        Args:
            value (str): The value to set or select

        Returns:
            bool: True if the value was successfully set, False otherwise

        Raises:
            ComboBoxItemNotFoundError: If the specified item is not found in a combobox
            ValueError: If there's an error setting the value for a text field
        """
        if not self.changeable:
            logger.info(f"Element {self.element.name} is not changeable")
            return False

        if self.type == "GuiComboBox":
            return self._select_from_combobox(value)

        try:
            self.element.text = value
            return True
        except Exception as e:
            logger.error(f"Error setting value for element {self.element.name}: {e}")
            raise ValueError(
                f"Error setting value for element {self.element.name}"
            ) from e

    def _select_from_combobox(self, item: str) -> bool:
        """
        Selects an item in a GuiComboBox element by matching its value.

        Args:
            item (str): The value of the item to select

        Returns:
            bool: True if the item was successfully selected

        Raises:
            ComboBoxItemNotFoundError: If the specified item is not found in the combobox
        """
        key = None
        for entry in self.element.entries:
            if entry.value.lower() == item.lower():
                key = entry.key
                break

        if not key:
            raise ComboBoxItemNotFoundError(f"Item: {item} not found in combobox")

        self.element.key = key
        return True

    def click(self) -> bool:
        """
        Clicks, presses, or selects the SAP element based on its type.

        This method performs the appropriate action for the following element types:
        - GuiButton: Presses the button
        - GuiTab: Selects the tab
        - GuiRadioButton: Selects the radio button
        - GuiCheckBox: Checks the checkbox

        Returns:
            bool: True after successfully performing the click action
        """
        try:
            if self.type == "GuiButton":
                self.element.press()
            elif self.type == "GuiTab":
                self.element.select()
            elif self.type == "GuiRadioButton":
                self.element.select()
            elif self.type == "GuiCheckBox":
                self.element.selected = True
        except Exception as e:
            logger.error(f"Error clicking element {self.element.name}: {e}")
            raise RuntimeError(f"Error clicking element {self.element.name}") from e

        return True

    def get_value(self) -> str:
        """
        Get the current value/text of the SAP element.

        Returns:
            str: The text value of the element
        """
        return str(self.text)
