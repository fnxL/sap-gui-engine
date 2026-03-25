import logging
from datetime import date
from typing import Any

from sap_gui_engine.constants import GuiObject, VKey
from sap_gui_engine.exceptions import SAPComboBoxOptionNotFound, SAPElementNotChangeable

logger = logging.getLogger(__name__)


class GuiVComponent:
    """
    Wrapper around the generatic SAP GUI visual component.
    Delegates attribute access to the underlying COM object while providing helper methods
    """

    def __init__(self, com_element: Any):
        self._com_element = com_element
        pass

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the underlying SAP element."""
        return getattr(self._com_element, name)

    @property
    def element(self) -> Any:
        """Access the raw COM element."""
        return self._com_element

    @property
    def text(self) -> str:
        """Gets the text property, stripped of whitespace."""
        # Use getattr to avoid failing if .text doesn't exist (though it usually does)
        val = getattr(self._com_element, "text", "")
        return str(val).strip()

    @text.setter
    def text(self, value: str) -> None:
        """
        Set the text of a GuiTextField or GuiCTextField.
        Also handles combobox selection automatically.

        Parameters
        ----------
        value : str
            The value to set or select
        """
        self.set_text(value, raise_error=True)

    def set_text(self, value: Any, raise_error: bool = False) -> bool:
        """
        Sets the text or selects a value for the component
        If value is of type date, it will be converted to a string format "dd.mm.yyyy" supported by SAP

        **Supported element types:**
            - GuiTextField
            - GuiCTextField
            - GuiPasswordField
            - GuiComboBox - Selects an item from the combobox by value


        Parameters
        ----------
        value : Any
            The string value or date object to set or select
        raise_error : bool, optional
            If true, raises exception when the element is read-only, by default False

        Returns
        -------
        bool
            True if the text was set successfully, False otherwise
        """

        if not self.changeable:
            msg = f"Element {self.name} ({self.type}) is not changeable."
            if raise_error:
                raise SAPElementNotChangeable(msg)

            logger.warning(msg)
            return False

        if isinstance(value, date):
            value = value.strftime("%d.%m.%Y")

        clean_value = str(value).strip()

        if self.type == GuiObject.COMBO_BOX:
            return self._select_combobox_entry(clean_value)

        max_length = getattr(self._com_element, "maxLength", None)

        if max_length and len(clean_value) > max_length:
            clean_value = clean_value[:max_length]

        self._com_element.text = clean_value
        return True

    def _select_combobox_entry(self, text: str) -> bool:
        """
        Selects a ComboBox entry by matching option's text (case-insensitive)

        Parameters
        ----------
        text : str
            Text of the option to select

        Returns
        -------
        bool
            True if selected
        """
        target = text.strip().lower()
        logger.debug(f"Target: {target}")
        for entry in self._com_element.entries:
            logger.debug(f"Entry: {entry.value.strip().lower()}")
            if str(entry.value).strip().lower() == target:
                self._com_element.key = entry.key
                return True

        raise SAPComboBoxOptionNotFound(
            f"Option '{text}' not found in ComboBox {self.name}"
        )

    def click(self) -> None:
        """
        Clicks/presses/selects the SAP element based on its type.

        This method performs the appropriate action for the following element types:
            - GuiButton: Presses the button
            - GuiTab: Selects the tab
            - GuiRadioButton: Selects the radio button
            - GuiCheckBox: Calling this method will toggle the checkbox
        """

        # Try standard methods
        if hasattr(self._com_element, "press"):
            self._com_element.press()
            return

        if hasattr(self._com_element, "select"):
            self._com_element.select()
            return

        # Checkboxes often use 'selected' property
        if hasattr(self._com_element, "selected"):
            self._com_element.selected = not self._com_element.selected
            return

        raise AttributeError(f"Element {self.name} ({self.type}) is not clickable.")

    def send_vkey(self, key: VKey | int) -> None:
        """Sends a virtual key to this element (usually a window)."""
        val = key.value if isinstance(key, VKey) else key
        self._com_element.sendVKey(val)

    def press(self):
        """Alias for click()"""
        return self.click()

    def select(self):
        """Alias for click()"""
        return self.click()
