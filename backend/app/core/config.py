from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SentinelOps AI"
    environment: str = "development"
    database_url: str = "postgresql+psycopg://sentinelops:sentinelops@db:5432/sentinelops"
    jwt_secret: str = "change-me-in-production-use-32-plus-random-chars"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def model_post_init(self, __context: object) -> None:
        if (
            self.environment.lower() == "production"
            and self.jwt_secret == "change-me-in-production-use-32-plus-random-chars"
        ):
            raise ValueError("A production JWT secret must be explicitly configured")


settings = Settings()
