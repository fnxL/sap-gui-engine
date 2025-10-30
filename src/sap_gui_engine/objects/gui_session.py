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

    def get_status_info(self) -> dict[str, Any] | None:
        """Gets current status bar information."""
        try:
            status_bar = self._session.findById("wnd[0]/sbar")
            return {
                "id": status_bar.MessageId,
                "text": status_bar.text,
                "type": status_bar.MessageType,
                "number": status_bar.MessageNumber,
                "is_popup": status_bar.MessageAsPopup,
                "parameter": status_bar.MessageParameter,
            }
        except Exception as e:
            logger.error(f"Error getting status bar information: {e}")
            return None

    def get_document_number(self) -> str:
        """Extracts document number from status bar when document is created successfully using va01 transaction."""
        status = self.get_status_info()
        try:
            return status["text"].split(" ")[3]
        except Exception as e:
            logger.error(f"Error getting document number: {status}")
            logger.error(e)
            raise e

    def dismiss_popups_until_none(self, key: VKey | int = VKey.ENTER):
        """
        Continuously dismisses popup dialogs by sending a specified virtual key (vkey)
        until no more popups appear. Assumes that the popup dialog is always the second
        window element (wnd[1]).

        Args:
            key: Virtual key to send to dismiss the popup dialog.

        """
        while True:
            try:
                self._session.findById("wnd[1]")
                self.sendVKey(key=key, window=1)
            except Exception as e:
                # No popup dialogs found, we can continue
                logger.debug(f"No more popup dialogs found: {e}")
                return
