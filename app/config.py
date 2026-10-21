from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://portal_app:CHANGE_ME@localhost:5432/controlm_portal"
    controlm_base_url: str = "https://CHANGE_ME:8443/automation-api"
    controlm_api_token: str = ""
    controlm_ca_bundle: str | None = None
    controlm_timeout_seconds: float = 15.0
    allow_dev_identity: bool = True
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
