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
    executable_path: str | None = None
    window_title_re: str | None = None


@pytest.fixture
def session() -> GuiSession:
    config = SAPConfig().model_dump()
    print(config)
    sap = SAPGuiEngine(**config)
    session = sap.open_connection()
    return session
