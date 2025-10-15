import pytest
from sap_gui_engine.sap_gui import SAPGuiEngine
from settings import TestSettings


@pytest.fixture(scope="session")
def test_settings():
    return TestSettings()


@pytest.fixture(scope="session")
def sap_engine(test_settings):
    return SAPGuiEngine(
        connection_name=test_settings.sap_connection_name,
        window_title=test_settings.sap_window_title,
        executable_path=test_settings.sap_executable_path,
    )


@pytest.mark.order(1)
def test_login_success(sap_engine: SAPGuiEngine, test_settings):
    result = sap_engine.login(
        username=test_settings.sap_username, password=test_settings.sap_password
    )
    assert result is True


def test_print():
    print("Hello World")
    assert True
