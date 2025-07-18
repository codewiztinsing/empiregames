import jwt
from ninja import NinjaAPI,Router
from ninja.security import django_auth
from .auth import encode_jwt,decode_jwt
from .schema import RegisterSchema, LoginSchema,UserSchema
from .models import User
from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model

from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from django.conf import settings

from pydantic import BaseModel
from typing import Optional, Union

users_router = Router()



@users_router.get("/refresh-token")
def refresh_access_token(request):
    return {"token": request.auth}



@users_router.post("/register")
def register(request, data: RegisterSchema):
    try:
        # Check if user already exists
        if User.objects.filter(phone=data.phone).exists():
            return {"success": False, "message": "Phone number already registered"}
        
        # Check if username already exists
        if User.objects.filter(username=data.username).exists():
            return JsonResponse({
                "success": False,
                "message": "Username already taken"
            }, status=400)

        # Create user with hashed password
        user = User.objects.create_user(
            username=data.username,
            phone=data.phone,
            telegram_id=data.telegram_id,
            password=make_password(data.password)
        )
        
        return {"success": True, "message": "User registered successfully"}
        
    except Exception as e:
        print("error = ",e)
        
        return {"success": False, "message": f"{e}"}



@users_router.post("/login")
def login(request, data: LoginSchema):
    try:
        user = User.objects.get(username=data.username)
        pasword = make_password(data.password)
        print("pasword = ",pasword)
        print("user.password = ",user.password)
      
        
        if pasword == user.password:
            # Generate JWT token
            payload = {
                'user_id': user.id,
                'username': user.username,
                'exp': datetime.utcnow() + timedelta(days=1),  # 1 day expiry
                'iat': datetime.utcnow()
            }
            
            print("user.password = ",user.password)
            token = jwt.encode(
                payload, 
                settings.SECRET_KEY, 
                algorithm='HS256'
            )
            print("token = ",token)
            
            return {
                "success": True,
                "message": "Login successful",
                "token": token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "phone": user.phone
                }
            }
        else:
            return {"success": False, "message": "Invalid credentials"}
            
    except Exception as e:
        return {"success": False, "message": "Login failed"}


# get user by telegram id
@users_router.get("/{telegram_id}",response=UserSchema)
def get_user_by_telegram_id(request,telegram_id:int):
    try:
        user = User.objects.get(telegram_id=str(telegram_id))
        return UserSchema.from_orm(user)
    except Exception as e:
        return {"success": False, "message": "User not found"}

    