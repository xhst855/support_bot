from pydantic import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    ZOHO_CLIENT_ID: str
    ZOHO_CLIENT_SECRET: str
    ZOHO_REFRESH_TOKEN: str
    CRYPTOAPIS_KEY: str
    DATABASE_URL: str = "sqlite:///db.sqlite3"
    BERT_SERVICE_URL: str = "http://bert_service:8000"
    ZOHO_DEPARTMENT_ID: str

    class Config:
        env_file = ".env"

settings = Settings()
