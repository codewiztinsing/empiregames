from ninja import Schema

class RegisterSchema(Schema):
    username: str
    password: str
    email: str
    phone: str
    telegram_id: str




class UserSchema(Schema):
    username: str
    email: str
    phone: str
    telegram_id: str
   


class LoginSchema(Schema):
    username: str
    password: str

