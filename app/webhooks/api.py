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
    print("data from direct charges = ",data)
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
    elif event_type == "charge.success":
        tx_ref = data.get("tx_ref")
        chapa_session = ChapaSession.objects.filter(tx_ref=tx_ref).first()
        if chapa_session:
            chapa_session.status = "success"
            chapa_session.save()
            user = User.objects.filter(phone=chapa_session.phone_number).first()
            if user:
                wallet = Wallet.objects.filter(user=user).first()
                if wallet:
                    wallet.balance = wallet.balance + float(chapa_session.amount)
                    wallet.save()
                    transaction = Transaction.objects.create(user=user,amount=chapa_session.amount,type="DEPOSIT",status="success",reference=chapa_session.tx_ref)
                    return JsonResponse({"message": "Callback received"}, status=200)
                else:
                    return JsonResponse({"message": "Wallet not found"}, status=404)
            else:
                return JsonResponse({"message": "User not found"}, status=404)  
            
            return JsonResponse({"message": "Callback received"}, status=200)
        else:
            return JsonResponse({"message": "Chapa session not found"}, status=404)
    else:
        return JsonResponse({"message": "Invalid event type"}, status=400)
       
   
