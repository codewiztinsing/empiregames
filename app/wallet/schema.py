from ninja import Schema

class ChapaSessionSchema(Schema):
    amount: float
    currency: str
    email: str
    first_name: str
    last_name: str
    phone_number: str
    tx_ref: str


class ChapaSessionResponseSchema(Schema):
    status: str=None
    message: str=None


class ChapaCallbackSchema(Schema):
    status: str=None
    ref_id: str=None
    tx_ref: str=None
    

class WalletSchema(Schema):
    action: str=None
    amount: float=None


class AddisPaySessionSchema(Schema):
    amount: float
    currency: str
    email: str
    first_name: str
    last_name: str
    phone_number: str
    tx_ref: str
    callback_url: str
    session_id: str=None

    def __init__(self, **data):
        print(f"AddisPaySessionSchema received data: {data}")
        super().__init__(**data)
   

class AddisPaySessionResponseSchema(Schema):
    status: str=None
    message: str=None

class AddisPayCallbackSchema(Schema):
    status: str=None
    ref_id: str=None
    tx_ref: str=None
    
    
    
    