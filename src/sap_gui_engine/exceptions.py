class TransactionError(Exception):
    """Raised when transaction code does not exist or Function is not possible."""


class LoginError(Exception):
    """Raised when login fails."""


class OptionNotFoundError(Exception):
    """Raised when an option is not found in a combobox."""


class TableConfigurationError(Exception):
    """Raised when there is an error while filling the table"""
