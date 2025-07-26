from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./jessai.db")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
