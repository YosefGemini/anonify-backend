import jwt

from datetime import datetime, timedelta

from conf import settings

from schemas.author import AuthorToken

from fastapi import Header, HTTPException,status
#from exceptions import AuthTokenMissing, AuthTokenExpired, AuthTokenCorrupted
from functions import auth_token


SECRET_KEY = settings.TOKEN_SECRET_KEY
ALGORITHM = settings.ALGORITHM


def generate_access_token(
        data: dict,
        expires_delta: timedelta = timedelta(
            minutes=settings.ACCESS_TOKEN_DEFAULT_EXPIRE_MINUTES
        )
):

    expire = datetime.utcnow() + expires_delta
    token_data = {
        **data,
        'exp': expire,
    }

    encoded_jwt = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    #r.sadd('access_tokens', encoded_jwt)

    return encoded_jwt

def decode_access_token(authorization: str = None):
    try:
        return jwt.decode(authorization, SECRET_KEY, algorithms=ALGORITHM)
    except Exception as e:
        print(e)
        return None

async def validate_token_header(
    Authorization: str = Header(),

) -> AuthorToken:
    try:
        
        authorization_token = Authorization.split(" ")[1] 
        # print("FASE 1",authorization_token)

        if not authorization_token:
            # print("CAMINO 1")

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")
        current_user = auth_token.decode_access_token(authorization_token)
        # if current_user == None:  # el token no es valido
        # print("FASE 2",current_user)
        if not current_user:  # el token no es valido
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        user_token = AuthorToken(**current_user)
        # print("TokenInfo:",user_token)
        return user_token
    except Exception as e:
        print("EXCEPCION:", e)
        raise HTTPException(status_code=400, detail=f"Token is missing: {e}")

    
