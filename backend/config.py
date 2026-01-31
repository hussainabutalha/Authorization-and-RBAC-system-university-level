from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str = "5432"
    JWT_SECRET: str
    REDIS_URL: str = "" # Optional for local dev without redis
    EMAIL_SERVICE: str = "gmail"
    EMAIL_USER: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_FROM: str = ""

    class Config:
        env_file = ".env" 
        extra = "ignore"

settings = Settings()
