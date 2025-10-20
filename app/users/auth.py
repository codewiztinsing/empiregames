import jwt
import os
import datetime
from ninja.security import HttpBearer
from django.conf import settings



# IMPORTANT: Use the same key used to sign tokens (users/api.py uses settings.SECRET_KEY)
jwt_secret = getattr(settings, "SECRET_KEY", None)

def decode_jwt(token):
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        # If nested under 'sub' (our encode_jwt), unwrap; else return payload as-is
        return payload.get("sub", payload)
    except Exception as e:
        print("[JWTDebug] decode_jwt error:", e)
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


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = decode_jwt(token)
            if not payload:
                print("[JWTDebug] authenticate failed: payload is None")
                return None
            # Attach to request for downstream usage if needed
            request.user_payload = payload
            return token
        except Exception as e:
            print("[JWTDebug] authenticate exception:", e)
            return None

