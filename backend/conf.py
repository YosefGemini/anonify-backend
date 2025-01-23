import os
from dotenv import load_dotenv



load_dotenv()

from pydantic import BaseSettings


class Settings(BaseSettings):
    ACCESS_TOKEN_DEFAULT_EXPIRE_MINUTES: int = 360
    #USERS_SERVICE_URL: str = os.environ.get('USERS_SERVICE_URL')
    #TX_SERVICE_URL: str = os.environ.get('TX_SERVICE_URL')
    #ORDERS_SERVICE_URL: str = os.environ.get('ORDERS_SERVICE_URL')
    GATEWAY_TIMEOUT: int = 59
    # Enviroment Variables
    CENTRAL_DATABASE_URL= os.getenv('CENTRAL_DATABASE_URL')
    CENTRAL_DATABASE_NAME= os.getenv('CENTRAL_DATABASE_NAME')
    AWS_STORAGE_BUCKET_NAME= os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_DEFAULT_REGION= os.getenv('AWS_DEFAULT_REGION')
    AWS_ACCESS_KEY_ID= os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY= os.getenv('AWS_SECRET_ACCESS_KEY')
    TOKEN_SECRET_KEY= os.getenv('TOKEN_SECRET_KEY')
    ALGORITHM= os.getenv('ALGORITHM')


settings = Settings()