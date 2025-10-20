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
    id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    telegram_id: Optional[str] = None
    games_played_this_week: Optional[int] = None
    remaining_games: Optional[int] = None
    total_referral_earnings: Optional[float] = None
    

class UpdateUserSchema(Schema):
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    telegram_id: Optional[str] = None

class ChangeSponsorSchema(Schema):
    referred_by: Optional[int] = None
    sponsor_changed: Optional[bool] = None


class TelegramUserSchema(Schema):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = False
    photo_url: Optional[str] = None


class TelegramAuthSchema(Schema):
    init_data: str
    user: TelegramUserSchema
    auth_date: int
    hash: str


class TelegramRegisterSchema(Schema):
    init_data: str
    user: TelegramUserSchema
    auth_date: int
    hash: str
    phone: Optional[str] = None
    referred_by: Optional[str] = None


class TelegramAuthResponseSchema(Schema):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[dict] = None
    is_new_user: Optional[bool] = False

