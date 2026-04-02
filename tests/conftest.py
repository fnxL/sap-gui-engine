import pytest
from pydantic_settings import BaseSettings, SettingsConfigDict

from sap_gui_engine import SAPGuiEngine
from sap_gui_engine.objects import GuiSession


class SAPConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.test", extra="ignore", env_prefix="SAP_"
    )
    connection_name: str
    username: str
    password: str
    client: str | None = None
    language: str | None = None
    executable_path: str = r"C:\Program Files\SAP\FrontEnd\SAPGUI\saplogon.exe"
    window_title_re: str = "SAP Logon 800"


@pytest.fixture(scope="session")
def session():
    config = SAPConfig().model_dump()
    print(config)
    sap = SAPGuiEngine(**config)
    session = sap.open_connection()
    yield session
    session.close()
