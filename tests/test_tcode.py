import pytest
from fixtures import *
from sap_gui_engine import SAPGuiEngine
from sap_gui_engine.exceptions import TransactionError


def test_tcode_success(engine: SAPGuiEngine):
    assert engine.start_transaction(tcode="va01") is True


def test_tcode_failure(engine: SAPGuiEngine):
    with pytest.raises(TransactionError, match="does not exist"):
        engine.start_transaction(tcode="invalid_tcode")
