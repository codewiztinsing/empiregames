import jwt
from ninja import NinjaAPI,Router
from ninja.security import django_auth
from .auth import encode_jwt,decode_jwt
from .schema import RegisterSchema, LoginSchema,UserSchema
# from .models import User
from django.db import IntegrityError
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from users.models import User
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from django.conf import settings
from wallet.models import Transaction,ChapaSession


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


@users_router.get("/{user_id}/daily-withdraw-limit")
def get_daily_withdraw_limit(request,user_id:int):
    try:
        user = User.objects.get(telegram_id=user_id)
        today = datetime.now().date()
        transactions = Transaction.objects.filter(user=user,type="WITHDRAW",created_at__date=today)
        daily_withdraw_limit = len(transactions)
        return {"daily_withdraw_limit": daily_withdraw_limit}
    except Exception as e:
        print("error = ",e)
        return {"success": False, "message": "Failed to get daily withdraw limit"}


@users_router.get("/{user_id}/number-of-game-played")
def get_number_of_game_played(request,user_id:int):
    try:
        print("user_id = ",user_id)
        user = User.objects.get(telegram_id=user_id)
        print("user = ",user)
        transactions = Transaction.objects.filter(user=user,type="BET")
        print("transactions = ",transactions)
        number_of_game_played = transactions.count()
        print("number_of_game_played = ",number_of_game_played)
        return {"number_of_game_played": number_of_game_played}
    except Exception as e:
        return {"success": False, "message": "Failed to get number of game played"}
    

@users_router.get("/{user_id}/number-of-game-won")
def get_number_of_game_won(request,user_id:int):
    try:
        user = User.objects.get(telegram_id=user_id)
        number_of_game_won = Transaction.objects.filter(user=user,type="WIN").count()
        return {"number_of_game_won": number_of_game_won}
    except Exception as e:
        return {"success": False, "message": "Failed to get number of game won"}    
# is deposited user
@users_router.get("/{user_id}/is-deposited")
def is_deposited(request, user_id: int):
    try:
        user = User.objects.get(telegram_id=user_id)
        print("phone ",user.phone)
        print("user ",user)
        # Check if user has any successful deposit transactions via ChapaSession
        has_deposited = ChapaSession.objects.filter(
            phone_number=user.phone)

        print("has deposited ",has_deposited)
        has_deposited = ChapaSession.objects.filter(
            phone_number=user.phone,
            status='success'
        ).exists()

        return {"is_deposited": has_deposited}
    except User.DoesNotExist:
        return {"success": False, "message": "User not found"}
    except Exception as e:
        print("error ",e)
        return {"success": False, "message": "Failed to check deposit status"}




