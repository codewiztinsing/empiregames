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
    event_type = data.get("event")
    if event_type == "payout.success":
        chapa_session = ChapaSession.objects.filter(reference=data.get("reference")).first()
        if chapa_session:
            chapa_session.status = data.get("status")
            chapa_session.save()
            return JsonResponse({"message": "Callback received"}, status=200)
        else:
            return JsonResponse({"message": "Chapa session not found"}, status=404)
    else:
        return JsonResponse({"message": "Invalid event type"}, status=400)
   
