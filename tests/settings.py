from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env.test", case_sensitive=False, extra="ignore"
    )
    sap_username: str
    sap_password: str
    sap_connection_name: str
    sap_window_title: str = "SAP Logon 770"
    sap_executable_path: str = (
        r"C:\Program Files (x86)\SAP\FrontEnd\SAPgui\saplogon.exe"
    )
