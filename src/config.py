from pydantic_settings import BaseSettings
from fastapi_users.jwt import SecretType

class BaseAppSettings(BaseSettings):
    class Config:
        env_file_encoding = 'utf-8'

class DatabaseSettings(BaseAppSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_NAME: str
    POSTGRES_USER: str
    POSTGRES_PASS: str
    
    class Config:
        env_file = './env/database.env'

class ProductionSettings(BaseAppSettings):
    SECRET_AUTH: SecretType
    HF_TOKEN: str

    class Config:
        env_file = './env/production.env'

database_settings = DatabaseSettings()
prod_settings = ProductionSettings()