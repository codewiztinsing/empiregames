import json
from django.shortcuts import render
from django.http import JsonResponse
from users.models import User
from wallet.models import Wallet,ChapaSession
from ninja import Router

webhooks_router = Router()

@webhooks_router.post("/")
def chapa_callback(request):
    data = json.loads(request.body.decode('utf-8'))
    print("data = ",data)
    print("Chapa callback request")
    
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=")
    return JsonResponse({"message": "Callback received"}, status=200)
