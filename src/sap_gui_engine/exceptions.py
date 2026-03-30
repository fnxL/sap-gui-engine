class SAPError(Exception):
    """Base exception for all SAP GUI Engine errors."""


class SAPConnectionError(SAPError):
    """Raised when connection establishment fails"""


class SAPElementNotFound(SAPError):
    """Raised when a requested GUI element is not found."""


class SAPElementNotChangeable(SAPError):
    """Raised when attempting to modify a read-only element."""


class SAPComboBoxOptionNotFound(SAPError):
    """Raised when a specified option is not available in a ComboBox."""


class SAPStatusBarError(SAPError):
    """Raised when there is an error in the status bar."""


class SAPTransactionError(SAPError):
    """Raised when a transaction fails to start or encounters a critical error."""


class SAPLoginError(SAPError):
    """Raised when the login process fails."""


class SAPElementTypeMismatch(SAPError):
    """Raised when the element type does not match the expected type."""
