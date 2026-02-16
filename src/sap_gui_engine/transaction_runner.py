import logging
from enum import StrEnum
from typing import Any, Callable, Optional

from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_fixed

from .constants import VKey
from .core import SAPGuiEngine
from .exceptions import (
    ActionConfigurationError,
    ElementConfigurationError,
    ScreenMappingError,
)

logger = logging.getLogger(__name__)


class ElementType(StrEnum):
    """Types of SAP GUI elements that can be interacted with."""

    TEXT = "text"
    COMBOBOX = "text"
    # Same API for text, ctext and comboboxes
    BUTTON = "click"
    CHECKBOX = "click"
    RADIO = "click"
    TAB = "click"
    # Same API (click) for buttons, checkboxes, tabs, and radios
    TABLE = "table"
    # Use this type when you are providing your own customn function to set the element.
    CALLABLE = "callable"


class Element(BaseModel):
    """Represents a SAP GUI element with its configuration."""

    id: str = Field(
        default="",
        description="ID of the SAP GUI element starting with wnd",
        pattern=r"^wnd",
    )
    type: ElementType = Field(
        default=ElementType.TEXT,
        description="Type of the element. Use callable type when passing your own function.",
    )
    name: str = Field(
        description="Name of the element. This name must match the 'key' in your data"
    )
    description: Optional[str] = Field(
        default=None, description="Description of the element"
    )
    func: Callable[[SAPGuiEngine, dict[str, Any]], None] | None = Field(
        default=None,
        description="Custom function for setting the element in SAP. "
        "Function signature: (SAPGuiEngine, dict[str, Any]) -> None",
    )


class ActionType(StrEnum):
    """Types of actions that can be performed in SAP GUI."""

    CLICK = "click"
    PRESS_ENTER = "press_enter"
    DISMISS_POPUPS = "dismiss_popups"
    BACK = "back"
    SEND_VKEY = "send_vkey"


class Action(BaseModel):
    """Represents an action to be performed in SAP GUI."""

    type: ActionType
    description: Optional[str] = Field(default=None, description="Action description")
    target_id: Optional[str] = Field(
        default=None, description="ID of the element to click if action type is CLICK"
    )
    vkey: Optional[int] = Field(
        default=None, description="Virtual key to send if action type is SEND_VKEY"
    )


class Screen(BaseModel):
    """Represents a SAP GUI screen or a tab with its elements and actions."""

    name: str
    description: Optional[str] = None
    elements: list[Element]
    on_entry: Optional[list[Action] | Action] = Field(
        default=None, description="Actions to perform to navigate to the screen"
    )
    on_exit: Optional[list[Action] | Action] = Field(
        default=None, description="Actions to perform after filling the screen"
    )
    press_enter: bool = Field(
        default=True, description="Whether to press enter after filling the screen"
    )


class ScreenOrderItem(BaseModel):
    name: str = Field(
        description="Name of the screen. This must match with the screen name defined in the screen_map provided to the TransactionRunner constructor."
    )
    table_columns: Optional[dict[str, list[str]]] = Field(
        default=None,
        description="Table name to list of columns to be used for filling the table. Name of the table must match with the name of the table defined in the elements of the screen_map. If not provided, all columns will be filled.",
    )


def _build_screen_order(
    screen_order: list[str | dict[str, Any]],
) -> list[ScreenOrderItem | Action]:
    result = []
    for screen in screen_order:
        if isinstance(screen, str):
            if screen.startswith("ACTION_"):
                parts = screen.split("_")
                action_type = parts[1].lower()
                if action_type == ActionType.CLICK:
                    target_id = parts[2]
                    result.append(
                        Action(
                            type=ActionType.CLICK,
                            target_id=target_id,
                        )
                    )
                action_type = "_".join(parts[1:]).lower()
                result.append(
                    Action(
                        type=ActionType(action_type),
                    )
                )
            else:
                result.append(ScreenOrderItem(name=screen))
        elif isinstance(screen, dict):
            result.append(ScreenOrderItem(**screen))

    return result


class TransactionRunner:
    """
    Executes SAP GUI transactions with automated data filling and navigation.

    This class handles transaction execution, data population, table filling,
    and error management for SAP GUI operations.
    """

    def __init__(
        self,
        sap: SAPGuiEngine,
        tcode: str,
        data: dict[str, Any] | list[dict[str, Any]],
        screen_map: dict[str, Screen],
        screen_order: Optional[list[str | dict[str, Any]]] = None,
        screen_data: Optional[dict[str, dict[str, Any]]] = None,
    ):
        """
        Parameters
        ----------
        sap : SAPGuiEngine
            The SAPGuiEngine instance for SAP GUI interaction
        tcode : str
            The transaction code to execute
        data : dict[str, Any] | list[dict[str, Any]]
            Data to fill into the transaction. Provide a list of dicts for screens
            with tables, or a single dict for simple field filling.
        screen_map : dict[str, Screen]
            Mapping of screen names to their Screen configurations
        screen_order : list[str | dict[str, Any]], optional
            Ordered list of screen names. If not provided, screens are processed in the order defined in screen_map. (Refer ScreenOrderItem)
        screen_data : dict[str, dict[str, Any]], optional
            Screen-specific data mapping. When provided, takes precedence over
            the data parameter for the specified screens.
        """
        # TODO: Support list[dict[str, Any]] for screen_data
        self.sap = sap
        self.tcode = tcode
        self.data = data
        self.screen_map = screen_map
        self.screen_order = _build_screen_order(screen_order) or _build_screen_order(
            list(screen_map.keys())
        )
        self.screen_data = screen_data
        self._processed_elements: set[str] = set()

    def run(self):
        self.sap.start_transaction(self.tcode)
        for item in self.screen_order:
            self._process_screen(item)

    def _process_screen(self, item: ScreenOrderItem | Action):
        """
        Process a single screen: navigates to the screen, fills data, and executes actions.

        Parameters
        ----------
        item : ScreenOrderItem | Action
            ScreenOrderItem or Action to process

        Raises
        ------
        ScreenMappingError
            If the screen mapping is not defined
        """
        if isinstance(item, Action):
            self._execute_actions(item)
            return

        screen = self.screen_map.get(item.name)
        if not screen:
            raise ScreenMappingError(
                f"Screen mapping not defined for screen: {item.name}"
            )

        logger.info(f"Processing screen: {screen.name}")
        current_data, line_items = self._get_data_for_screen(screen)

        if not self._data_is_in_screen(screen, current_data):
            logger.info(
                f"Skipping screen: {screen.name} - no data to fill for this screen"
            )
            return

        if screen.on_entry:
            logger.info(f"Executing on_entry actions for screen: {screen.name}")
            self._execute_actions(screen.on_entry)

        self._fill_screen(
            screen=screen,
            data=current_data,
            line_items=line_items,
            table_columns=item.table_columns,
        )

        if screen.on_exit:
            logger.info(f"Executing on_exit actions for screen: {screen.name}")
            self._execute_actions(screen.on_exit)

    def _get_data_for_screen(self, screen: Screen):
        """
        Retrieves data for a specific screen. If screen does not have data, it will use the data provided in the constructor.

        Parameters
        ----------
        screen_name : str
            Name of the screen

        Returns
        -------
        tuple[dict[str, Any], list[dict[str, Any]]]
            A tuple containing (current_data, line_items) where:
            - current_data: Single dict for field filling
            - line_items: List of dicts for table filling
        """
        data = (
            self.screen_data.get(screen.name) if self.screen_data else None
        ) or self.data

        if isinstance(data, list):
            current_data = data[0] if data else {}
            line_items = data
        else:
            current_data = data
            line_items = [data]

        return current_data, line_items

    def _data_is_in_screen(self, screen: Screen, data: dict[str, Any]) -> bool:
        """
        Check if the screen has at least one field with available data and is not none.

        Parameters
        ----------
        screen : Screen
            The screen to check
        data : dict[str, Any]
            The data dictionary to check against

        Returns
        -------
        bool
            True if at least one element in the screen is present in data
            or if the screen contains a table element
        """
        for element in screen.elements:
            if element.type == ElementType.TABLE:
                return True

            if data.get(element.name):
                return True

        return False

    def _fill_screen(
        self,
        screen: Screen,
        data: dict[str, Any],
        line_items: list[dict[str, Any]],
        table_columns: Optional[dict[str, list[str]]] = None,
    ):
        """
        Fill all elements in the screen with provided data.
        Will not process element name that occur twice in the entire screen map

        Parameters
        ----------
        screen : Screen
            The screen to fill
        data : dict[str, Any]
            Field data for simple elements
        line_items : list[dict[str, Any]]
            Line items for table elements
        table_columns : dict[str, list[str]], optional
            Table name to list of columns to be used for filling the table. Name of the table must match with the name of the table defined in the elements of the screen_map. If not provided, all columns will be filled.

        Raises
        ------
        ElementConfigurationError
            If element configuration is invalid
        SAPStatusBarError
            If SAP status bar indicates an error after filling
        """
        for element in screen.elements:
            if element.name in self._processed_elements:
                logger.info(
                    f"Skipping duplicate element name: {element.name} in screen: {screen.name} as it was already processed in some other screen"
                )
                continue
            if element.type == ElementType.TEXT:
                result = self._fill_text(element, data, screen.name)
                if result:
                    self._processed_elements.add(element.name)
            elif element.type == ElementType.CALLABLE:
                if element.func is None:
                    raise ElementConfigurationError(
                        f"Function is required for callable element: {element.name}"
                    )
                # Call user defined function with the data
                # TODO: Send line_items as well to the function
                element.func(self.sap, data)
                self._processed_elements.add(element.name)
            elif element.type == ElementType.TABLE:
                logger.info(
                    f"Filling table: {element.name} with {len(line_items)} rows "
                    f"in screen: {screen.name}"
                )
                table_cols = table_columns.get(element.name)
                if table_cols:
                    logger.debug(f"Using columns: {table_cols}")

                self.sap.find_by_id(element.id).fill(
                    data=line_items, columns=table_cols
                )
                self._processed_elements.add(element.name)
            else:
                raise ElementConfigurationError(f"Unknown element type: {element.type}")

        # Press enter after filling all fields in the screen
        if screen.press_enter:
            logger.info(f"Pressing enter for screen: {screen.name}")
            self.sap.press_enter()
            self.sap.dismiss_popups()
            self.sap.raise_for_status()

    @retry(reraise=True, stop=stop_after_attempt(4), wait=wait_fixed(1))
    def _fill_text(self, element: Element, data: dict[str, Any], screen_name: str):
        try:
            value = data.get(element.name)
            if value is not None and element.name in data:
                logger.info(
                    f"Setting element: '{element.name}' in screen: '{screen_name}' to value: {value}"
                )
                sap_el = self.sap.find_by_id(element.id, raise_error=False)
                if not sap_el:
                    logger.warning(
                        f"Element {element.name} not found in current screen: {screen_name}, skipping data entry for this element"
                    )
                    return False
                sap_el.text = value
                return True
        except Exception as e:
            self.sap.press_enter()
            raise e

    def _execute_actions(self, actions: list[Action] | Action) -> None:
        """Execute one or more actions

        Parameters
        ----------
        actions : list[Action] | Action
            Action or a list of actions to execute

        Raises
        ------
        ActionConfigurationError
            If action configuration is invalid
        """
        action_list = [actions] if isinstance(actions, Action) else actions

        for action in action_list:
            logger.info(
                f"Executing {action.type} action"
                + (f": {action.description}" if action.description else "")
            )
            if action.type == ActionType.CLICK:
                if action.target_id is None:
                    raise ActionConfigurationError(
                        f"Target ID is required for click action for click action: {action.description}"
                    )

                target = self.sap.find_by_id(action.target_id, raise_error=False)

                if not target:
                    logger.warning(
                        f"Target element '{action.target_id}' not found. Assuming already executed entry action."
                    )
                else:
                    target.click()
            elif action.type == ActionType.PRESS_ENTER:
                self.sap.press_enter()
            elif action.type == ActionType.DISMISS_POPUPS:
                self.sap.dismiss_popups()
            elif action.type == ActionType.BACK:
                self.sap.send_vkey(VKey.F3)
            elif action.type == ActionType.SEND_VKEY:
                if action.vkey is None:
                    raise ActionConfigurationError(
                        f"Virtual key is required for send_vkey action: {action.description}"
                    )
                self.sap.send_vkey(action.vkey)
            else:
                raise ActionConfigurationError(f"Unknown action type: {action.type}")
