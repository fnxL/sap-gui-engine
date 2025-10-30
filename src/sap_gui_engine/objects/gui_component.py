import logging
from ..exceptions import OptionNotFoundError
from typing import Any

logger = logging.getLogger(__name__)


class GuiComponent:
    def __init__(self, element: Any):
        self.element = element
        self.type = element.type
        self.changeable = element.changeable
        self._text = element.text

    @property
    def text(self):
        return self.text

    @text.setter
    def text(self, value: str):
        """
        Sets or selects a text value for supported SAP element types.

        This method will only operate on changeable elements. For unchangeable elements, it logs an info message and returns.

        Supported element types:
        - GuiTextField: Sets the text property
        - GuiPasswordField: Sets the text property
        - GuiCTextField: Sets the text property
        - GuiComboBox: Selects an item from the combobox by value

        Args:
            value (str): The value to set or select

        Raises:
            ComboBoxOptionNotFoundError: If the specified item is not found in a combobox
            ValueError: If there's an error setting the value for a text field
        """
        if not self.changeable:
            logger.info(f"Element {self.element.name} is not changeable")
            return

        if self.type == "GuiComboBox":
            return self._select_combobox_entry_by_text(value)

        self.element.text = value
        return

    def click(self):
        """
        Clicks, presses, or selects the SAP element based on its type.

        This method performs the appropriate action for the following element types:
        - GuiButton: Presses the button
        - GuiTab: Selects the tab
        - GuiRadioButton: Selects the radio button
        - GuiCheckBox: Calling this method will toggle the checkbox
        """
        for method in ("press", "select"):
            if hasattr(self.element, method):
                getattr(self.element, method)()
                return

        if hasattr(self.element, "selected"):
            current = getattr(self.element, "selected")
            setattr(self.element, "selected", not current)
            return

        raise AttributeError(
            f"{self.__class__.__name__} has no clickable method (.press/.select)"
        )

    def press(self):
        return self.click()

    def select(self):
        return self.click()

    def sendVKey(self, key: int):
        self.element.sendVKey(key)

    def _select_combobox_entry_by_text(self, text: str) -> bool:
        """
        Selects an entry in GuiComboBox element by matching its text.

        Args:
            text (str): The text value of the entry to select

        Returns:
            bool: True if the entry was successfully selected

        Raises:
            OptionNotFoundError: If the specified item is not found in the combobox
        """
        key = None
        for entry in self.element.entries:
            if entry.value.lower() == text.lower():
                key = entry.key
                break

        if not key:
            raise OptionNotFoundError(f"Entry: {text} not found in combobox")

        self.element.key = key
        # TODO: Find a way to update/refresh the internal element / reinstantiate the Component

        return True
