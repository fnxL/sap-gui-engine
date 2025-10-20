# SAP GUI Engine

A Python framework for interacting with the SAP GUI Scripting API. This library provides a high-level, object-oriented interface to automate SAP GUI interactions, making it easier to build robust SAP automation solutions.

## Features

- **Easy SAP Connection Management**: Automatically handles launching SAP, connecting to sessions, and managing connections
- **Intuitive Element Interaction**: Find and interact with SAP GUI elements using a clean, consistent API
- **Comprehensive Element Support**: Support for various SAP GUI controls including text fields, combo boxes, buttons, tabs, radio buttons, and checkboxes
- **Virtual Key Support**: Send virtual key commands (F1-F12, Ctrl+combinations, etc.) to SAP windows
- **Robust Login Handling**: Built-in login functionality with error handling for common login scenarios
- **Transaction Management**: Start and manage SAP transactions with proper error handling
- **Status Information Retrieval**: Access SAP status bar information for monitoring and validation

## Installation

```bash
pip install sap-gui-engine
```

## Requirements

- Python 3.10+
- SAP GUI Scripting enabled
- SAP Logon 770+ or higher

## Quick Start

```python
from sap_gui_engine import SAPGuiEngine, VKey

# Initialize the SAP GUI Engine
sap = SAPGuiEngine(
    connection_name="Your SAP Connection Name",  # Name of your SAP connection
    window_title="SAP Logon Pad",               # Window title of SAP Logon
    executable_path="C:/Program Files (x86)/SAP/SAPGUI770/SAPlogon.exe"  # Path to SAP executable
)

# Perform login
sap.login(
    username="your_username",
    password="your_password"
)

# Start a transaction
sap.start_transaction("va01")  # Create Sales Order transaction

# Interact with SAP elements
customer_element = sap.findById("wnd[0]/usr/subSUBSCREEN_HEADER:SAPMV45A:4701/ctxtKUAGV-KUNNR")
customer_element.set_text("102133")

# Send virtual keys
sap.sendVKey(VKey.ENTER)

# Click buttons
sap.findById("wnd[0]/tbar[0]/btn[15]").click()  # Save button

# Close connection when done
sap.close_connection()
```

## Core Components

### SAPGuiEngine

The main class that orchestrates SAP interactions. It handles:

- Launching SAP application
- Establishing connections
- Managing sessions
- Providing access to SAP elements and functionality

### SAPElement

A wrapper class that provides a consistent interface for interacting with different types of SAP controls:

- **Text Fields**: Set text values using `set_text()`
- **Combo Boxes**: Select options by text value using `set_text()`
- **Buttons**: Click using `click()`
- **Tabs**: Select using `click()`
- **Radio Buttons**: Select using `click()`
- **Checkboxes**: Toggle using `click()`

### VKey

An enum representing SAP virtual keys, making it easy to send keyboard commands:

```python
from sap_gui_engine import VKey

# Examples
sap.sendVKey(VKey.ENTER)
sap.sendVKey(VKey.SAVE)      # Ctrl+S
sap.sendVKey(VKey.F2)
sap.sendVKey(VKey.REFRESH)   # Ctrl+R
```

## Advanced Usage

### Custom Login Elements

If your SAP system uses different element IDs for login, you can customize the login process:

```python
from sap_gui_engine.mappings.login import LoginScreenElements

custom_login_elements = LoginScreenElements(
    username="wnd[0]/usr/txtCUSTOM-USERNAME",  # Your custom username element ID
    password="wnd[0]/usr/pwdCUSTOM-PASSWORD"   # Your custom password element ID
)

sap.login(
    username="your_username",
    password="your_password",
    login_screen_elements=custom_login_elements
)
```

### Working with Different SAP Windows

SAP applications can have multiple windows. You can specify which window to interact with:

```python
# Send a key to window 1 (popup dialog)
sap.sendVKey(VKey.ENTER, window=1)

# Find an element in window 1
element = sap.findById("wnd[1]/usr/txtSAPLSMTR_NAVIGATION-1")
```

### Handling SAP Elements

```python
# Find an element
element = sap.findById("wnd[0]/usr/ctxtVBAK-VKORG")

# Check element properties
print(f"Element name: {element.name}")
print(f"Element type: {element.type}")
print(f"Is changeable: {element.changeable}")

# Get text value
current_text = element.get_text()

# Set text for text fields
element.set_text("New Value")

# Click elements (buttons, tabs, radio buttons, checkboxes)
element.click()
```

## Supported SAP GUI Controls

The framework supports interaction with various SAP GUI controls:

- **GuiTextField**: Text input fields
- **GuiCTextField**: Character text fields
- **GuiComboBox**: Dropdown lists
- **GuiButton**: Buttons
- **GuiTab**: Tab controls
- **GuiRadioButton**: Radio buttons
- **GuiCheckBox**: Checkboxes
- **GuiLabel**: Read-only labels

## Error Handling

The framework includes specific exceptions for common SAP automation scenarios:

- `LoginError`: Raised when login fails
- `TransactionError`: Raised when a transaction code doesn't exist
- `ComboBoxOptionNotFoundError`: Raised when a requested option is not found in a combobox

```python
from sap_gui_engine.exceptions import LoginError, TransactionError, ComboBoxOptionNotFoundError

try:
    sap.login(username="user", password="pass")
except LoginError as e:
    print(f"Login failed: {e}")

try:
    sap.start_transaction("invalid_tcode")
except TransactionError as e:
    print(f"Transaction error: {e}")

try:
    combo_element.set_text("Non-existent option")
except ComboBoxOptionNotFoundError as e:
    print(f"Combo box error: {e}")
```
## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions about using the SAP GUI Engine, please open an issue in the GitHub repository.
