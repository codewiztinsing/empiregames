from ninja import NinjaAPI,Router
from .schema import ChapaSessionSchema, ChapaSessionResponseSchema, ChapaCallbackSchema,WalletSchema
from .models import ChapaSession, Wallet,Transaction
from django.http import JsonResponse
from utils import generate_reference
from users.models import User
import sys
import json
router = Router()

@router.get("/")
def index():
    return "Hello, World!"

@router.post("/chapa/create-session")
def create_chapa_session(request, data: ChapaSessionSchema):
    try:
        chapa_session = ChapaSession.objects.create(
        amount=data.amount,
        status="PENDING",
        currency=data.currency,
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        phone_number=data.phone_number,
        tx_ref=data.tx_ref,
        callback_url=data.callback_url,
        return_url=data.return_url,
        customization=data.customization
    )
       
        return 200,ChapaSessionResponseSchema(
            session_id=chapa_session.id or None,
            status=chapa_session.status or None,
            message="Session created successfully"
            )
    except Exception as e:
        print("error = ",e)
        return JsonResponse({"error": str(e)}, status=400)

# /api/v1/webhook/chapa/callback/??
@router.get("/webhook/chapa/callback/")

def chapa_callback(request):
    data = json.loads(request.body.decode('utf-8'))
    chapa_session = ChapaSession.objects.filter(tx_ref=data.get("trx_ref")).first()
    phone_number = chapa_session.phone_number
    user = User.objects.filter(phone=phone_number).first()
    if chapa_session and user:
        chapa_session.status = data.get("status")
        if  data.get("status") == "success":
            wallet = Wallet.objects.get(user=user)
            wallet.balance += float(chapa_session.amount)
            wallet.save()
      

        return JsonResponse({"message": "Callback received"}, status=200)
    else:
        return JsonResponse({"message": "Session not found"}, status=404)



# get player wallet balance
@router.get("/player/{telegram_id}")
def player_wallet(request,telegram_id:int):
    try:
        user = User.objects.get(telegram_id=telegram_id)
        print("user = ",user)
        wallet = Wallet.objects.get(user=user)
        return JsonResponse({"balance": wallet.balance}, status=200)
    except Exception as e:
        print("error = ",e)
        return JsonResponse({"error": str(e)}, status=400)
    

  
@router.put("/player/{telegram_id}/")
def update_player_wallet(request,telegram_id:int, data: WalletSchema):
    try:
        user = User.objects.get(telegram_id=telegram_id)
        wallet = Wallet.objects.get(user=user)
        wallet_balance = wallet.balance
        if data.action == "withdraw":
            wallet_balance -= float(data.amount)
            transaction = Transaction.objects.create(user=user,amount=data.amount,type="WITHDRAW",status="pending",reference=generate_reference())
        elif data.action == "deposit":
            transaction = Transaction.objects.create(user=user,amount=data.amount,type="DEPOSIT",status="pending",reference=generate_reference())
            wallet_balance += float(data.amount)
        wallet.balance = wallet_balance
        wallet.save()
        return JsonResponse({"message": "Wallet updated successfully"}, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
