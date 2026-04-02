import pytest

from sap_gui_engine import GuiSession
from sap_gui_engine.exceptions import SAPTransactionError


def test_tcode_success(session: GuiSession):
    assert session.start_transaction(tcode="va01") is True


def test_tcode_failure(session: GuiSession):
    with pytest.raises(SAPTransactionError, match="does not exist"):
        session.start_transaction(tcode="invalid_tcode")


def test_status_info(session: GuiSession):
    status = session.get_statusbar_msg()
    assert "does not exist" in status.text
