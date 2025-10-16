import pytest
from settings import Settings
from sap_gui_engine import SAPGuiEngine
from sap_gui_engine.exceptions import LoginError

@pytest.mark.order(1)
def test_login_failure(engine: SAPGuiEngine, config: Settings):
    engine.close_connection()
    engine.open_connection(config.sap_connection_name)
    with pytest.raises(LoginError, match="password is incorrect"):
        engine.login(username="invalid", password="invalid")


@pytest.mark.order(2)
def test_login_success(engine: SAPGuiEngine, config: Settings):
    result = engine.login(username=config.sap_username, password=config.sap_password)
    assert result is True
