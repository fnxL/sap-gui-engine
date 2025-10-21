import logging
from typing import Any
from sap_gui_engine.exceptions import ComboBoxOptionNotFoundError
from .gui_vcomponent import GuiVComponent

logger = logging.getLogger(__name__)


class SAPGuiElement(GuiVComponent):
    """
    A wrapper class for SAP GUI Objects that provides a consistent interface
    for interacting with different types of SAP GUI Components.

    This class abstracts the underlying SAP GUI element and provides methods
    to perform common operations like setting values and clicking elements.
    """

    def __init__(self, element: Any):
        super().__init__(element)
        self._text = str(element.text).strip()  # This is read-write

    @property
    def text(self) -> str:
        """
        Gets or sets the text of the component, depending on the type of object.

        Returns:
            str: The text value of the component, which depends on the type of object

        Note: The value of this property depends on the type of the object on which it is called.
        This is obvious for text fields or menu items. On the other hand this property is empty
        for toolbar buttons and is the class id for shells. You can read the text property of
        a label, but you can't change it, whereas you can only set the text property of a
        password field, but not read it.
        """
        return self._text

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
        if not self._changeable:
            logger.info(f"Element {self._element.name} is not changeable")
            return

        # TODO: Add support for selecting combobox entry by value
        if self._type == "GuiComboBox":
            return self._select_combobox_entry_by_text(value)

        try:
            self._element.Text = value
            # Update internal text value after setting
            self._text = str(self._element.text).strip()
            return
        except Exception as e:
            logger.error(f"Error setting text for element {self._element.name}: {e}")
            raise ValueError(
                f"Error setting text for element {self._element.name}"
            ) from e

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

    def _select_combobox_entry_by_text(self, text: str) -> bool:
        """
        Selects an entry in GuiComboBox element by matching its text.

        Args:
            text (str): The text value of the entry to select

        Returns:
            bool: True if the entry was successfully selected

        Raises:
            ComboBoxOptionNotFoundError: If the specified item is not found in the combobox
        """
        key = None
        for entry in self._element.entries:
            if entry.value.lower() == text.lower():
                key = entry.key
                break

        if not key:
            raise ComboBoxOptionNotFoundError(f"Entry: {text} not found in combobox")

        self._element.key = key
        # TODO: Find a way to update/refresh the internal _element / reinstantiate the VComponent

        return True
