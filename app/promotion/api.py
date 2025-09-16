from ninja import Router
from .models import Banner
from .forms import BannerForm
from dashboard.tasks import send_message_to_all_players
from rest_framework.response import Response
from rest_framework import status
promotion_router = Router()

@promotion_router.post("/upload_banner/", response=BannerForm)
def upload_banner(request):
    form = BannerForm(request.POST, request.FILES)
    if form.is_valid():
        banner = form.save(commit=False)
        banner.save()
        return banner
    else:
        return form.errors


@promotion_router.post("/broadcast/")
def broadcast_message(request):
    message = request.POST.get('message')
    send_message_to_all_players.delay(message)
    return Response({"message": "Message broadcasted successfully"}, status=status.HTTP_200_OK)
   
