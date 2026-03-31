# SAP Gui Engine

A Python framework for interacting with the SAP GUI Scripting API. This library provides a high-level, object-oriented interface to automate SAP GUI interactions, making it easier to build robust SAP automation solutions.

## Table of Contents
- [Requirements](#requirements)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
  - [SAPGuiEngine](#sapguiengine)
  - [GuiSession](#guisession)
  - [GuiTableControl](#guitablecontrol)
  - [Virtual Keys (VKey)](#virtual-keys-vkey)
- [Examples](#examples)
- [Error Handling](#error-handling)
- [License](#license)

## Requirements

- Python 3.11+
- SAP GUI Scripting enabled
- SAP Logon 770 Patch Level 0 or higher
- Windows OS (uses Windows COM objects)

## Installation

```sh
pip install sap-gui-engine
```


## Features

- **Automatic SAP Connection Management**: Launch SAP Logon automatically if not running, connect to the scripting engine, open or attach to existing session, handle user login automatically, handle popup dialogs automatically, all of this with just one method `.open_connection()`
- **Object-oriented Interface**: Clean, intuitive object-oriented interface for SAP components that abstracts away the complexity of the underlying COM objects
- **Unified Text Input API**: Unified API `.set_text("value")` or `.text = "value"` that handles GuiTextFields, GuiPasswordFields, GuiComboBox selection by name of the entry and more parameters to `.set_text()`
- **Unified Click API**: Unified API `.click()` that handles GuiButton, GuiRadioButton, GuiCheckBox, GuiTabStrip, etc. Aliases provided `.press()`, `.select()`
- **Advanced Table Operations**: Easy data entry to GuiTableControl by using `.fill()` method that handles whether to overwrite or fill data in empty table, automatic pagination, handles popups, etc.
- **Comprehensive Error Handling**: Specific exception classes for different error conditions to enable robust error handling

## Usage

### SAPGuiEngine
The `SAPGuiEngine` class is the main entry point for connecting to the SAP Gui Scripting Engine.


```python
SAPGuiEngine(
    connection_name: str,
    username: str,
    password: str,
    client: str | None = None,
    terminate_other_sessions: bool = True,
    language: str | None = None,
    executable_path: str = r"C:\Program Files\SAP\FrontEnd\SAPGUI\saplogon.exe",
    window_title_re: str = "SAP Logon 800"
)
```

**Parameters:**
- `connection_name`: Name of the SAP connection to connect to
- `username`: Username for SAP login
- `password`: Password for SAP login
- `client`: Client number for SAP login (optional)
- `terminate_other_sessions`: Whether to terminate other sessions when multi-logon is detected (default: True)
- `language`: Language code for SAP login (optional)
- `executable_path`: Path to SAP Logon executable (default: standard SAP installation path). Change this according to your SAP Logon installation
- `window_title_re`: Regular expression for SAP Logon window title (default: "SAP Logon 800"). Change this according to your SAP Logon version

### Basic Connection

```python
from sap_gui_engine import SAPGuiEngine

# Initialize the SAP GUI Engine
sap = SAPGuiEngine(
    connection_name="340 Quality",
    username="your_username",
    password="your_password",
)
# Open a connection to SAP
session = sap.open_connection()

# Perform operations with the session
session.start_transaction("SE16N")

# Receive a GuiVComponent object
# Perform operations on this element based on it's type
element = session.find_by_id("wnd[0]/element_id")

# Handles setting text for GuiTextField, GuiCTextField, GuiCombobox, etc
element.text = "Value" # or element.set_text("Value")

session.press_enter()
session.raise_for_status() # Raise error if error in status bar message.

session.send_vkey(VKey.PAGE_DOWN) # Refer VKey for all key mapping

# By default, dismiss_popups() send enter key presses indefinitely to the wnd[1] if it is a popup window.
session.dismiss_popups()
# To limit this, provide limit=10. It will try to dismiss the popup 10 times and exit.
session.dismiss_popups(limit=10)
```

### Working with tables
```python
from sap_gui_engine import SAPGuiEngine

sap = SAPGuiEngine(
    connection_name="MySystem",
    username="myuser",
    password="mypassword",
)

session = sap.open_connection()
session.start_transaction("SE16N")
# Navigate to the screen where the table control is located
# ...
```
Assuming we have the table data as follows
```python
table_data = [
    {"Material": "MAT001", "Quantity": "Material 1"},
    {"Material": "MAT002", "Quantity": "Material 2"},
]
```
Find the table control and fill/overwrite the table with the data
```python
table_control = session.find_by_id("wnd[0]/usr/cntlGRID1/shellcont/shell")
# Fill the table with data
table_control.fill(data=table_data)
```
You can select only the table headers that you want to fill
```python
table_control.fill(data=table_data, headers=["Material"])
```
This would only fill the Material column and leave the Quantity column empty. This way you can restrict the filling/overwriting to specific columns. The header name must also match with the header in the SAP table.

If you want to set_focus() to the element before setting the value
```python
table_control.fill(data=table_data, headers=["Material"], set_focus=True)
```
## API Reference

### SAPGuiEngine

The main class for connecting to SAP systems.

#### Constructor
```python
SAPGuiEngine(
    connection_name: str,
    username: str,
    password: str,
    client: str | None = None,
    terminate_other_sessions: bool = True,
    language: str | None = None,
    executable_path: str = r"C:\Program Files\SAP\FrontEnd\SAPGUI\saplogon.exe",
    window_title_re: str = "SAP Logon 800"
)
```

**Parameters:**
- `connection_name`: Name of the SAP connection to connect to
- `username`: Username for SAP login
- `password`: Password for SAP login
- `client`: Client number for SAP login (optional)
- `terminate_other_sessions`: Whether to terminate other sessions when multi-logon is detected (default: True)
- `language`: Language code for SAP login (optional)
- `executable_path`: Path to SAP Logon executable (default: standard SAP installation path)
- `window_title_re`: Regular expression for SAP Logon window title (default: "SAP Logon 800")

#### Methods

##### `open_connection() -> GuiSession`
Opens a connection to the SAP system. This method tries to find existing open connections of the given user and attaches to the first session of the connection. If no open connection is found, it tries to open a new connection, perform login and returns the GuiSession object.

**Returns:** `GuiSession` - The GuiSession object of the opened/existing connection to interact with the session.

**Raises:**
- `SAPConnectionError` - If connection fails to open or login fails
- `SAPLoginError` - If login fails
- `TimeoutError` - If SAP Logon application fails to launch within timeout (default: 60 seconds)

##### `close_connection()`
Closes the SAP connection including all sessions. This method closes the SAP connection and all associated sessions, and cleans up the internal references to the SAP GUI objects.

### GuiSession

Wrapper class for SAP GUI COM Session objects that provides convenient methods for common operations. Delegates attribute access that are not available in this wrapper to the underlying SAP COM object.

#### Methods

##### `find_by_id(id: str, raise_error: bool = True) -> Optional[GuiVComponent | GuiTableControl]`
Finds a GUI component by its SAP ID.

**Parameters:**
- `id`: The ID of the GUI element
- `raise_error`: If True, raises SAPElementNotFound if missing (default: True)

**Returns:** `Optional[GuiVComponent | GuiTableControl]` - GuiVComponent wrapper or GuiTableControl wrapper or None if not found (and raise_error is False)

**Raises:**
- `SAPElementNotFound` - If the element is not found and raise_error is True

##### `send_vkey(key: VKey | int, window_index: int = 0, repeat_count: int = 1)`
Sends a VKey to a specific SAP window.

**Parameters:**
- `key`: The virtual key to send
- `window_index`: Index of the SAP window (default: 0)
- `repeat_count`: Number of times to send the key (default: 1)

**Raises:**
- `SAPElementNotFound` - If the window is not found

##### `press_enter(window_index: int = 0, repeat_count: int = 1)`
Helper method to send the ENTER virtual key to a window.

##### `dismiss_popups(key: VKey = VKey.ENTER, window_index: int = 1)`
Dismisses popup dialogs until there are no popups by sending a specific key to the popup window.

**Parameters:**
- `key`: The key to send to dismiss the popup (default: VKey.ENTER)
- `window_index`: The index of the popup dialog window (default: 1)

##### `get_statusbar_msg() -> StatusbarMsg`
Retrieves the current status bar message.

**Returns:** `StatusbarMsg` - The StatusbarMsg dataclass

**Raises:**
- `SAPElementNotFound` - If the statusbar is not found in the window

##### `raise_for_status(message: str | None = None, exception: Exception = SAPStatusBarError) -> StatusbarMsg`
Checks the status bar for error message type and raises the given exception.

**Parameters:**
- `message`: Optional message to prepend to the error message (default: None)
- `exception`: The exception object to raise (default: SAPStatusBarError)

##### `raise_if_error_dialog(window_index: int = 1, exception=SAPTransactionError, message="Error dialog detected")`
Checks for error dialogs and raises an exception if found.

**Parameters:**
- `window_index`: Index of the window to check (default: 1)
- `exception`: Exception to raise if error dialog is found (default: SAPTransactionError)
- `message`: Message to include in the exception (default: "Error dialog detected")

##### `maximize()`
Maximizes the main window.

##### `start_transaction(tcode: str)`
Starts a new transaction. Ends any current transaction first.

**Parameters:**
- `tcode`: Code of the transaction to start

**Raises:**
- `SAPTransactionError` - If transaction code does not exist or Function is not possible

##### `end_transaction()`
Ends the current SAP transaction (equivalent to /n).

##### `get_session_info() -> SessionInfo`
Returns information about the current session.

**Returns:** `SessionInfo` - A dataclass containing session information.

##### `close_session()`
Closes the current session.

### GuiTableControl

Specialized class for handling SAP table controls with advanced features for data manipulation.

#### Properties

##### `visible_rows: int`
Returns the number of visible rows in the table.

#### Methods

##### `get_table_headers(headers: list[str] | None = None, exclude_headers: list[str] | None = None, lowercase: bool = True) -> dict[str, int]`
Creates a mapping of table headers (lowercase by default) to header index.

**Parameters:**
- `headers`: List of headers to include. If None, all headers of the table are included (default: None)
- `exclude_headers`: List of headers to exclude. If None, no headers are excluded (default: None)
- `lowercase`: Whether to return the lowercase headers (default: True)

**Returns:** `dict[str, int]` - Mapping of header name to header index

**Raises:**
- `ValueError` - If both headers and exclude_headers are specified

##### `fill(data: list[dict[str, Any]], headers: list[str] | None = None, exclude_headers: list[str] | None = None, set_focus: bool = False)`
Fills or overwrites GuiTableControl table with the provided data. Each item in the data must be of type `{header_name: value_to_set_or_overwrite}`. This function handles pagination, dismisses popups, checks for the status bar for any errors, after each page.

**Parameters:**
- `data`: Data to fill/overwrite the table with
- `headers`: Select the headers to fill/overwrite, the headers must match and be consistent the keys in the data. If None, it will consider all the headers in the table to fill/overwrite (default: None)
- `exclude_headers`: List of headers to exclude. If None, no headers are excluded (default: None)
- `set_focus`: Focus on the element before filling/overwriting (default: False)

**Raises:**
- `ValueError` - If both headers and exclude_headers are specified
- `ValueError` - If provided data is empty

### Virtual Keys (VKey)

Enumeration of SAP Virtual Key codes for keyboard simulation.

Available keys include:
- `VKey.ENTER` (0)
- `VKey.F1` to `VKey.F12` (1-12)
- `VKey.CTRL_S` (11)
- `VKey.SHIFT_F1` to `VKey.SHIFT_F12` (13-24)
- `VKey.CTRL_F1` to `VKey.CTRL_F12` (25-36)
- `VKey.CTRL_SHIFT_F1` to `VKey.CTRL_SHIFT_F12` (37-48)
- `VKey.CTRL_E`, `VKey.CTRL_F`, etc. (70+)
