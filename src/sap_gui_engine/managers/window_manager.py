import logging
from typing import Any
from sap_gui_engine.vkey import VKey
from sap_gui_engine.objects import SAPGuiElement
from sap_gui_engine.exceptions import TransactionError

logger = logging.getLogger(__name__)


class SAPWindowManager:
    def __init__(self, session):
        self._session = session

    def maximize(self, window: int = 0) -> None:
        """Maximizes the specified SAP window."""
        try:
            self._session.findById(f"wnd[{window}]").maximize()
        except Exception as e:
            logger.error(f"Error maximizing window {window}: {e}")
            raise RuntimeError(f"Error maximizing window: {window}")

    def send_vkey(self, key: VKey, window: int = 0, times: int = 1) -> bool:
        """Sends a virtual key to a window."""
        try:
            for _ in range(times):
                self._session.findById(f"wnd[{window}]").sendVKey(key.value)
            return True
        except Exception as e:
            logger.error(f"Error sending vkey {key} to window {window}: {e}")
            raise RuntimeError(f"Error sending vkey {key} to window {window}")

    def start_transaction(self, tcode: str, new_transaction: bool = True) -> bool:
        """Starts a SAP transaction."""
        if new_transaction:
            self._session.StartTransaction(tcode)
        else:
            self._session.SendCommand(tcode)

        status = self.get_status_info()
        if status and "does not exist" in status["text"].lower():
            logger.error(status["text"])
            raise TransactionError(status["text"])

        return True

    def find_element(self, element_id: str):
        """Finds an SAP element by ID."""
        try:
            return SAPGuiElement(self._session.findById(element_id))
        except Exception as e:
            logger.error(f"Error getting element {element_id}: {e}")
            raise RuntimeError(f"Error getting element {element_id}")

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
