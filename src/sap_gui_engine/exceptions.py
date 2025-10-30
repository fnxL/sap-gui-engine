class TransactionError(Exception):
    """Raised when transaction code does not exist or Function is not possible."""

    pass


class LoginError(Exception):
    """Raised when login fails."""

    pass
