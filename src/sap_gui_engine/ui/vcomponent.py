import logging
from datetime import date
from typing import TYPE_CHECKING, Any

from ..constants import GuiObject, VKey
from ..exceptions import ComboBoxOptionNotFound, SAPElementNotChangeable

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..core import SAPGuiEngine


class GuiVComponent:
    """
    Wrapper around the a generatic SAP GUI visual component.
    Delegates attribute access to the underlying COM object while providing helper methods
    """

    def __init__(self, element: Any, __parent_class__: "SAPGuiEngine" = None):
        """
        Parameters
        ----------
        element : Any
            The raw COM object of the element.

        _parent_class_ : Any, optional
            The parent class that creates this instance, by default None
        """
        self._element = element
        self.__class = __parent_class__

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the underlying SAP element."""
        return getattr(self._element, name)

    @property
    def element(self) -> Any:
        """Access the raw COM element."""
        return self._element

    @property
    def text(self) -> str:
        """Gets the text property, stripped of whitespace."""
        # Use getattr to avoid failing if .text doesn't exist (though it usually does)
        val = getattr(self._element, "text", "")
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

        max_length = getattr(self._element, "maxLength", None)

        if max_length and len(clean_value) > max_length:
            clean_value = clean_value[:max_length]

        self._element.text = clean_value
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
        for entry in self._element.entries:
            logger.debug(f"Entry: {entry.value.strip().lower()}")
            if str(entry.value).strip().lower() == target:
                self._element.key = entry.key
                return True

        raise ComboBoxOptionNotFound(
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
        if hasattr(self._element, "press"):
            self._element.press()
            return

        if hasattr(self._element, "select"):
            self._element.select()
            return

        # Checkboxes often use 'selected' property
        if hasattr(self._element, "selected"):
            self._element.selected = not self._element.selected
            return

        raise AttributeError(f"Element {self.name} ({self.type}) is not clickable.")

    def send_vkey(self, key: VKey | int) -> None:
        """Sends a virtual key to this element (usually a window)."""
        val = key.value if isinstance(key, VKey) else key
        self._element.sendVKey(val)

    def press(self):
        """Alias for click()"""
        return self.click()

    def select(self):
        """Alias for click()"""
        return self.click()
