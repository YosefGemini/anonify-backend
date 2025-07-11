import os
from dotenv import load_dotenv
from typing import ClassVar


load_dotenv()

# from pydantic import BaseSettings

# cambios de pydantic a pydantic_settings en nueva version a partir de python 3.11
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ACCESS_TOKEN_DEFAULT_EXPIRE_MINUTES: int = 360
    #USERS_SERVICE_URL: str = os.environ.get('USERS_SERVICE_URL')
    #TX_SERVICE_URL: str = os.environ.get('TX_SERVICE_URL')
    #ORDERS_SERVICE_URL: str = os.environ.get('ORDERS_SERVICE_URL')
    GATEWAY_TIMEOUT: int = 59
    # Enviroment Variables
    CENTRAL_DATABASE_URL: ClassVar[str]= os.getenv('CENTRAL_DATABASE_URL')
    CENTRAL_DATABASE_NAME: ClassVar[str]= os.getenv('CENTRAL_DATABASE_NAME')
    AWS_STORAGE_BUCKET_NAME: ClassVar[str]= os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_DEFAULT_REGION: ClassVar[str]= os.getenv('AWS_DEFAULT_REGION')
    AWS_ACCESS_KEY_ID: ClassVar[str]= os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY: ClassVar[str]= os.getenv('AWS_SECRET_ACCESS_KEY')
    TOKEN_SECRET_KEY: ClassVar[str]= os.getenv('TOKEN_SECRET_KEY')
    ALGORITHM: ClassVar[str]= os.getenv('ALGORITHM')
    UPLOAD_DIRECTORY: ClassVar[str]= os.getenv('UPLOAD_DIRECTORY')
    


settings = Settings()