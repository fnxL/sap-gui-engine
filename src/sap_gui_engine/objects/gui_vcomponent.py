import logging
from datetime import date
from typing import Any

from sap_gui_engine.constants import GuiObject, VKey
from sap_gui_engine.exceptions import (
    SAPComboBoxOptionNotFound,
    SAPElementNotChangeable,
    SAPElementTypeMismatch,
)

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

    def get_text(self, strip_text: bool = True) -> str:
        """
        Gets the text property of the element

        Parameters
        ----------
        strip_text : bool, optional
            Wehther to strip the leading and trailling whitespaces of the text, by default True

        Returns
        -------
        str
        """
        if strip_text:
            return str(self.text).strip()

        return self.text

    def set_text(
        self,
        value: Any,
        raise_error: bool = False,
        date_format: str = "%d.%m.%Y",
        set_focus: bool = False,
        strip_value: bool = True,
    ) -> bool:
        """
        Sets the text or selects a value for the component
        If value is of type date, it will be converted to a string format "dd.mm.yyyy" by default as supported by SAP. Pass date_format parameter to convert to custom format.

        If the length of the value exceeds the maxLength property of the element, it will be truncated to fit maxLength characters of the element.

        **Supported element types:**
            - GuiTextField
            - GuiCTextField
            - GuiPasswordField
            - GuiComboBox - Selects an item from the combobox by value (case-insensitive)


        Parameters
        ----------
        value : Any
            The string value or date object to set or select
        raise_error : bool, optional
            If true, raises exception when the element is read-only (not changeable), by default False
        date_format : str, optional
            The format to use when converting a date object to a string, by default "%d.%m.%Y"
        set_focus : bool, optional
            If true, sets focus to the element before setting the text, by default False
        strip_value: bool, optional
            If true, strips leading and trailing whitespaces from the value before setting it, by default True

        Returns
        -------
        bool
            True if the text was set successfully, False otherwise

        Raises
        ------
        SAPElementNotChangeable
            If the element is not changeable and raise_error is True
        """
        if not self.changeable:
            msg = f"Element {self.name} ({self.type}) is not changeable."
            if raise_error:
                raise SAPElementNotChangeable(msg)

            logger.warning(msg)
            return False

        if isinstance(value, date):
            value = value.strftime(date_format)

        if strip_value:
            value = str(value).strip()

        if self.type == GuiObject.COMBO_BOX:
            return self._select_combobox_entry(value)

        max_length = getattr(self._com_element, "maxLength", None)

        if max_length and len(value) > max_length:
            value = value[:max_length]

        if set_focus:
            self._com_element.SetFocus()

        self._com_element.text = value
        return True

    def select_combobox(
        self,
        entry_name: str,
        raise_error: bool = False,
        set_focus: bool = False,
        strip_value: bool = True,
    ) -> bool:
        """
        Alias for set_text for selecting combobox entries.
        """
        return self.set_text(
            value=entry_name,
            raise_error=raise_error,
            set_focus=set_focus,
            strip_value=strip_value,
        )

    def get_checkbox_state(self) -> bool:
        """
        Returns the state of the checkbox field

        Returns
        -------
        bool
            True, if checkbox is selected, False otherwise.

        Raises
        ------
        SAPElementTypeMismatch
            If the element is not a checkbox.
        """
        if self.type != GuiObject.CHECKBOX:
            raise SAPElementTypeMismatch(
                f"Element {self.name} is not a checkbox. It is a {self.type}"
            )
        return bool(self._com_element.selected)

    def set_focus(self):
        """
        Sets focus on the element
        """
        self._com_element.SetFocus()

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
