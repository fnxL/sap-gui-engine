import pytest
from settings import Settings
from sap_gui_engine import SAPGuiEngine
from sap_gui_engine.exceptions import LoginError, TransactionError
from fixtures import *


@pytest.mark.order(1)
def test_login_failure(engine: SAPGuiEngine):
    with pytest.raises(LoginError):
        engine.login(username="invalid", password="invalid")


@pytest.mark.order(2)
def test_login_success(engine: SAPGuiEngine, config: Settings):
    result = engine.login(username=config.sap_username, password=config.sap_password)
    assert result is True


def test_tcode_success(engine: SAPGuiEngine):
    assert engine.start_transaction(tcode="va01") is True


def test_tcode_failure(engine: SAPGuiEngine):
    with pytest.raises(TransactionError):
        engine.start_transaction(tcode="invalid_tcode")
