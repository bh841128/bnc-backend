from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = (
        "mysql+pymysql://demo:demo@127.0.0.1:3306/ecommerce_demo?charset=utf8mb4"
    )
    jwt_secret: str = "dev-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    cors_origins: str = (
        "http://localhost:5173,http://localhost:5174,"
        "http://127.0.0.1:5173,http://127.0.0.1:5174"
    )

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
