from ninja import Schema
from typing import Optional

class RegisterSchema(Schema):
    username: str
    password: str
    email: str
    phone: str
    telegram_id: str
    referred_by: Optional[str] = None




class UserSchema(Schema):
    username: str
    email: str
    phone: str
    telegram_id: str
   


class LoginSchema(Schema):
    username: str
    password: str

class UserResponseSchema(Schema):
    success: bool
    message: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    telegram_id: Optional[str] = None
    games_played_this_week: Optional[int] = None
    remaining_games: Optional[int] = None

