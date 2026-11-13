from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Yarmarka CRM API"
    database_url: str = "postgresql+psycopg2://yarmarka:yarmarka_dev_only@db:5432/yarmarka"
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    bootstrap_admin_login: str = ""
    bootstrap_admin_password: str = ""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
