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
        self.element = element
        self.name = element.name
        self.type = element.type
        self.text = str(element.text).strip()
        self.changeable = element.changeable
        if self.type == "GuiComboBox":
            self.key = element.key

    def get_text(self) -> str:
        """
        Get the current value/text of the SAP element.

        Returns:
            str: The text value of the element
        """
        return str(self.text)

    def set_text(self, text: str) -> bool:
        """
        Sets or selects a text value for supported SAP element types.

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
            ComboBoxOptionNotFoundError: If the specified item is not found in a combobox
            ValueError: If there's an error setting the value for a text field
        """
        if not self.changeable:
            logger.info(f"Element {self.element.name} is not changeable")
            return False

        if self.type == "GuiComboBox":
            return self._select_from_combobox(text)

        try:
            self.element.text = text
            return True
        except Exception as e:
            logger.error(f"Error setting text for element {self.element.name}: {e}")
            raise ValueError(
                f"Error setting text for element {self.element.name}"
            ) from e

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
        for entry in self.element.entries:
            if entry.value.lower() == text.lower():
                key = entry.key
                break

        if not key:
            raise ComboBoxOptionNotFoundError(f"Option: {text} not found in combobox")

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
