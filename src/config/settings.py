from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Naviconomy"
    db_driver: str = "postgresql+asyncpg"
    db_user: str = "postgres"
    db_password: SecretStr
    db_host: SecretStr
    db_port: int = 5432
    db_name: str = "postgres"

    secret_key: SecretStr = SecretStr("unsafe-key")
    algorithm: SecretStr = SecretStr("HS256")
    access_token_expire_minutes: int = 30
    max_connections_count: int = 20
    min_connections_count: int = 1
    debug: bool = False

    @property
    def database_url(self) -> SecretStr:
        return SecretStr(
            f"{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
