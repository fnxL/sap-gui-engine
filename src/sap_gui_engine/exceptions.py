"""Custom exceptions for the SAP GUI Engine."""


class SAPError(Exception):
    """Base exception for all SAP GUI Engine errors."""


class SAPTransactionError(SAPError):
    """Raised when a transaction fails to start or encounters a critical error."""


class SAPElementNotFound(SAPError):
    """Raised when a requested GUI element is not found."""


class SAPElementNotChangeable(SAPError):
    """Raised when attempting to modify a read-only element."""


class SAPLoginError(SAPError):
    """Raised when the login process fails."""


class ComboBoxOptionNotFound(SAPError):
    """Raised when a specified option is not available in a ComboBox."""


class SAPTableConfigurationError(SAPError):
    """Raised when there is a mismatch or error in table configuration/population."""


class ScreenMappingError(Exception):
    """Raised when the screen is not defined in the screen map."""


class SAPStatusBarError(SAPError):
    """Raised when there is an error in the status bar."""


class ElementConfigurationError(Exception):
    """Raised when element configuration is invalid"""


class ActionConfigurationError(Exception):
    """Raised when action configuration is invalid"""
