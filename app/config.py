from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:55432/module14_db"
    JWT_SECRET_KEY: str = "change-me-in-production-use-a-long-random-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    model_config = SettingsConfigDict(env_file=("local.env", ".env"))


settings = Settings()
