from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DATABASE: str = "fresh_delivery"

    class Config:
        env_file = ".env"


settings = Settings()
