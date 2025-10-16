import pytest
from sap_gui_engine import SAPGuiEngine
from sap_gui_engine.exceptions import TransactionError


def test_tcode_success(engine: SAPGuiEngine):
    assert engine.start_transaction(tcode="va01") is True


def test_tcode_failure(engine: SAPGuiEngine):
    with pytest.raises(TransactionError, match="does not exist"):
        engine.start_transaction(tcode="invalid_tcode")

def test_status_info(engine: SAPGuiEngine):
    status = engine.get_status_info()
    assert "does not exist" in status["text"]
