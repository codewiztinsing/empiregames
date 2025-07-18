from ninja import Schema

class ChapaSessionSchema(Schema):
    amount: float
    currency: str
    email: str
    first_name: str
    last_name: str
    phone_number: str
    tx_ref: str
    callback_url: str
    return_url: str
    customization: dict


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
    
    
    