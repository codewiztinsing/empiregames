import json
from django.shortcuts import render
from django.http import JsonResponse
from users.models import User
from wallet.models import Wallet,ChapaSession,Transaction
from ninja import Router

webhooks_router = Router()

@webhooks_router.post("/")
def chapa_callback(request):
    data = json.loads(request.body.decode('utf-8'))
    event_type = data.get("event")
    if event_type == "payout.success":
        account_number = data.get("account_number")
        user = User.objects.filter(phone=account_number).first()
        if user:
            wallet = Wallet.objects.filter(user=user).first()
            if wallet:
                wallet.balance = wallet.balance - float(data.get("amount"))
                wallet.save()
                transaction = Transaction.objects.create(user=user,amount=data.get("amount"),type="WITHDRAW",status="success",reference=data.get("reference"))
                return JsonResponse({"message": "Callback received"}, status=200)
            else:
                return JsonResponse({"message": "Wallet not found"}, status=404)
        else:
            return JsonResponse({"message": "User not found"}, status=404)
    else:
        return JsonResponse({"message": "Invalid event type"}, status=400)
       
   
