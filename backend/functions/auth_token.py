import jwt

from datetime import datetime, timedelta

from conf import settings
#from exceptions import AuthTokenMissing, AuthTokenExpired, AuthTokenCorrupted



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

    
    
