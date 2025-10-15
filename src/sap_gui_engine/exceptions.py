class LoginError(Exception):
    pass


class ComboBoxItemNotFoundError(Exception):
    """Raised when a requested item is not found in a combobox."""
    pass

class TransactionError(Exception):
    """Raised when transaction code does not exist."""
    pass
