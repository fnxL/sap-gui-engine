import pytest
from sap_gui_engine.sap_gui import SAPGuiEngine
from settings import Settings


@pytest.fixture(scope="session")
def config():
    return Settings()


@pytest.fixture(scope="session")
def engine(config: Settings):
    engine =  SAPGuiEngine(
        connection_name=config.sap_connection_name,
        window_title=config.sap_window_title,
        executable_path=config.sap_executable_path,
    )
    engine.close_connection()
    engine.open_connection(config.sap_connection_name)
    yield engine
