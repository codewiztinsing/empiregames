import jwt
import os
import datetime
from ninja.security import HttpBearer



jwt_secret = os.getenv("JWT_SECRET")

def decode_jwt(token):
    try:
        token = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        return token
    except Exception as e:
        print("error = ",e)
        return None
  

def encode_jwt(payload):
    try:
        payload = {
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "sub": payload
        }
        return jwt.encode(payload, jwt_secret, algorithm="HS256")
    except Exception as e:
        print("error = ",e)
        return None


def verify_jwt(token):
    try:
        return decode_jwt(token)
    except jwt.InvalidTokenError:
        return None
    except jwt.ExpiredSignatureError:
        return None

