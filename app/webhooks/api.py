import json
from django.shortcuts import render
from django.http import JsonResponse
from users.models import User
from wallet.models import Wallet,Transaction
from ninja import Router
from webhooks.tasks import handle_deposit_success

webhooks_router = Router()

@webhooks_router.post("/")
def callbacks_disabled(request):
    return JsonResponse({"message": "Legacy callbacks disabled"}, status=410)
       
   
