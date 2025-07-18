from ninja import NinjaAPI,Router
from .schema import ChapaSessionSchema, ChapaSessionResponseSchema, ChapaCallbackSchema,WalletSchema
from .models import ChapaSession, Wallet,Transaction
from django.http import JsonResponse
from utils import generate_reference
from users.models import User
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
        trx_ref=data.trx_ref,
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
    print("data = ",request.GET.get("trx_ref"))
    print("status = ",request.GET.get("status"))
    chapa_session = ChapaSession.objects.filter(trx_ref=request.GET.get("trx_ref")).first()
    if chapa_session:
        chapa_session.status = request.GET.get("success")
        if request.GET.get("status") == "success":
            transaction = Transaction.objects.get(reference=request.GET.get("trx_ref"))
            transaction.type = "DEPOSIT"
            transaction.status = "success"
            transaction.save()

        chapa_session.save()

            

    return JsonResponse({"message": "Callback received"}, status=200)



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
