from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from fastapi_users.jwt import SecretType

load_dotenv()

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASS: str
    SECRET_AUTH: SecretType
    debug: bool

    class Config:
        env_file = '.env'
        extra = 'allow' # allow additional states in .env files
        env_file_encoding = 'utf-8'

settings = Settings()