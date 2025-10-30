import logging
from typing import Any
from ..exceptions import TransactionError
from .gui_component import GuiComponent
from ..mappings import VKey

logger = logging.getLogger(__name__)


class GuiSession:
    def __init__(self, session: Any):
        self._session = session

    def maximize(self):
        """Maximizes the main SAP window"""
        try:
            self._session.findById("wnd[0]").maximize()
        except Exception as e:
            logger.error(f"Error maximizing window 0: {e}")
            raise RuntimeError(f"Error maximizing window 0: {e}")

    def start_transaction(self, tcode: str) -> bool:
        """
        Starts a new SAP transaction.
        Args:
            tcode: Transaction code to start.

        Returns:
            True if transaction started successfully

        Raises:
            TransactionError: If transaction code does not exist or Function is not possible.

        Note: This will end any existing transaction without saving your work. Use this with caution.
        """
        self._session.StartTransaction(tcode)

        status = self.get_status_info()
        if status and "does not exist" in status["text"].lower():
            logger.error(status["text"])
            raise TransactionError(status["text"])

        return True

    def end_transaction(self) -> bool:
        """Ends the current SAP transaction. Calling this function has the same effect as SendCommand("/n")."""
        self._session.EndTransaction()
        return True

    def findById(self, id: str):
        return GuiComponent(self._session.findById(id))

    def sendVKey(self, key: VKey, window: int = 0, times: int = 1) -> bool:
        """
        Sends a virtual key to a window.
        Args:
            key: Virtual key to send.
            window: Window to send the key to.
            times: Number of times to send the key.

        Returns:
            True if key sent successfully.

        Raises:
            RuntimeError: If key could not be sent.
        """
        try:
            for _ in range(times):
                self._session.findById(f"wnd[{window}]").sendVKey(key.value)
            return True
        except Exception as e:
            logger.error(f"Error sending vkey {key} to window {window}: {e}")
            raise RuntimeError(f"Error sending vkey {key} to window {window}")
