import re
import requests
from ninja import NinjaAPI,Router
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import ManualSession
from decouple import config
from .schema import (ChapaSessionSchema,
    ChapaSessionResponseSchema, 
    ChapaCallbackSchema,
    WalletSchema, 
    AddisPaySessionSchema,
    AddisPaySessionResponseSchema,
    AddisPayCallbackSchema
 )
from .models import ChapaSession, Wallet,Transaction, AddisPaySession
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
        tx_ref=data.tx_ref
    )
       
        return JsonResponse({
            "session_id": chapa_session.id or None,
            "status": chapa_session.status or None,
            "message": "Session created successfully"
        }, status=200)
    except Exception as e:
        print("error = ",e)
        return JsonResponse({"error": str(e)}, status=400)

# /api/v1/webhook/chapa/callback/
@router.get("/webhook/chapa/callback/")
@csrf_exempt
def chapa_callback(request):
    # For GET requests, data comes in query parameters, not request body
    trx_ref = request.GET.get("trx_ref")
    status = request.GET.get("status")
    
    if not trx_ref or not status:
        return JsonResponse({"message": "Missing required parameters"}, status=400)
    
    chapa_session = ChapaSession.objects.filter(tx_ref=trx_ref).first()
    if not chapa_session:
        print("Chapa session not found")
        return JsonResponse({"message": "Session not found"}, status=404)
    
    phone_number = chapa_session.phone_number
    user = User.objects.filter(phone=phone_number).first()
    if not user:
        print("User not found")
        return JsonResponse({"message": "User not found"}, status=404)
    
    chapa_session.status = status
    if status == "success":
        wallet = Wallet.objects.get(user=user)
        wallet.balance += float(chapa_session.amount)
        wallet.save()
        chapa_session.status = "success"
        chapa_session.save()
        print("Payment processed successfully")

    return JsonResponse({"message": "Callback received"}, status=200)



# get player wallet balance
@router.get("/player/{telegram_id}")
def player_wallet(request,telegram_id:int):
    try:
        user = User.objects.filter(telegram_id=telegram_id).first()
        print("user = ",user)
        wallet = Wallet.objects.filter(user=user).first()
        print("wallet = ",wallet)
        return JsonResponse({"balance": wallet.balance if wallet else 0}, status=200)
    except Exception as e:
        print("error = ",e)
        return JsonResponse({"error": str(e)}, status=400)
    

  
@router.put("/player/{telegram_id}/")
def update_player_wallet(request,telegram_id:int, data: WalletSchema):
    try:
        user = User.objects.filter(telegram_id=telegram_id).first()
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



@router.post("/addispay/create-session")
def create_addispay_session(request, data: AddisPaySessionSchema):
    try:
        addispay_session = AddisPaySession.objects.create(
            amount=data.amount,
            status="PENDING",
            currency=data.currency,
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            phone_number=data.phone_number,
            tx_ref=data.tx_ref,
            callback_url=data.callback_url,
            session_id=data.session_id
          
        )
        return JsonResponse({
            "session_id": addispay_session.id or None,
            "status": addispay_session.status or None,
            "message": "Session created successfully"
        }, status=200)
    except Exception as e:
        print("error = ",e)
        return JsonResponse({"error": str(e)}, status=400)
    

@router.post("/webhook/addispay/callback/success/")
@csrf_exempt
def addispay_callback(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        print("AddisPay callback data:", data)
        
        if data.get("payment_status") == "success":
            addispay_session = get_object_or_404(AddisPaySession, session_id=data.get("session_uuid"))
            print("addispay_session = ",addispay_session)
            phone_number = addispay_session.phone_number
            user = get_object_or_404(User, phone=phone_number)
            wallet = get_object_or_404(Wallet, user=user)
            wallet.balance += float(addispay_session.amount)
            wallet.save()
            addispay_session.status = data.get("payment_status")
            addispay_session.save()
            print("AddisPay payment processed successfully")
            return JsonResponse({"message": "Callback received"}, status=200)
        else:
            print(f"AddisPay payment failed with status: {data.get('payment_status')}")
            return JsonResponse({"message": "Payment failed"}, status=400)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Error parsing AddisPay callback data: {e}")
        return JsonResponse({"message": "Invalid callback data"}, status=400)
    except Exception as e:
        print(f"Error processing AddisPay callback: {e}")
        return JsonResponse({"message": "Error processing callback"}, status=500)
    

# /api/v1/wallet/webhook/manual/error/

@router.post("/manual/callback/success/")
@csrf_exempt
def manual_success(request):
    print("Manual success request")
    try:
        data = json.loads(request.body.decode('utf-8'))
        print("data = ",data)
        session_id = data.get("session_id")
        status = data.get("status")
        print("status = ",status)
        # Extract payer number from either top-level or nested 'data'
        details = data.get("data") or {}
        transaction_number = details.get("transaction_number")
        payer_telebirr_no = data.get("payer_telebirr_no") or details.get("payer_telebirr_no") or details.get("credited_account")
        print("payer_telebirr_no = ", payer_telebirr_no)
        if not payer_telebirr_no:
            return JsonResponse({"message": "Missing payer_telebirr_no"}, status=400)
        # Keep only digits to handle masked numbers like 2519****1912
        digits_only = re.sub(r"\D", "", payer_telebirr_no)
        last_payer_4_digits = digits_only[-4:]
      
        
        if status == "success":
            manual_session = ManualSession.objects.filter(session_id=session_id).first()
            
            if not manual_session:
                print("No manual session found for session id:", session_id)
                return JsonResponse({"message": "No matching session found"}, status=404)
            
            print("Found manual session:", manual_session)
            
            if manual_session.status == "success":
                # Transaction already processed
                user = User.objects.filter(phone=manual_session.phone_number).first()
                if user and user.telegram_id:
                    try:
                        bot_token = config('BOT_TOKEN')
                        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                        message = f"⚠️ Transaction Already Processed!\n\n💰 Amount: {manual_session.amount} ETB\n🔗 Reference: {manual_session.session_id}\n\nThis payment has already been credited to your wallet."
                        telegram_payload = {
                            'chat_id': user.telegram_id,
                            'text': message,
                            'parse_mode': 'HTML'
                        }
                        requests.post(telegram_url, json=telegram_payload)
                        print(f"Notified user {user.telegram_id} about duplicate transaction")
                    except Exception as notification_error:
                        print(f"Failed to notify user about duplicate transaction: {notification_error}")
                return JsonResponse({"message": "Already processed"}, status=200)
            
            # Process the successful payment
            user = get_object_or_404(User, phone=manual_session.phone_number)
            wallet = get_object_or_404(Wallet, user=user)
            wallet.balance += float(manual_session.amount)
            wallet.save()
            manual_session.status = "success"
            manual_session.save()
            transaction = Transaction.objects.create(
                user=user,
                amount=manual_session.amount,
                type="DEPOSIT",
                status="success",
                reference=manual_session.session_id
            )
            transaction.save()
            
            # Notify user about successful deposit
            if user.telegram_id:
                try:
                    bot_token = config('BOT_TOKEN')
                    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    message = f"🎉 Deposit Successful! 🎉\n\n💰 Amount: {manual_session.amount} ETB\n📊 New Balance: {wallet.balance} ETB\n🔗 Reference: {manual_session.session_id}\n\n✅ Your account has been credited successfully!"
                    telegram_payload = {
                        'chat_id': user.telegram_id,
                        'text': message,
                        'parse_mode': 'HTML'
                    }
                    requests.post(telegram_url, json=telegram_payload)
                    print(f"Notified user {user.telegram_id} about successful deposit")
                except Exception as notification_error:
                    print(f"Failed to notify user about successful deposit: {notification_error}")
            
            return JsonResponse({"message": "Manual success processed"}, status=200)
        else:
            manual_session = ManualSession.objects.filter(session_id=session_id).first()
            manual_session.status = "failed"
            manual_session.save()
            return JsonResponse({"message": "Manual failed data"}, status=200)
    except Exception as e:
        print(f"Error processing Manual success: {e}")
        return JsonResponse({"message": "Error processing success"}, status=500)

@router.post("/manual/callback/error/")
@csrf_exempt
def manual_error(request):
    print("Manual error request")
    try:

        data = json.loads(request.body.decode('utf-8'))
        session_id = data.get("session_id")
        status = data.get("status")
        print("Manual error data:", data)
    except Exception as e:
        print(f"Error processing Manual error: {e}")
        return JsonResponse({"message": "Error processing error"}, status=500)    


@router.post("/manual/session/")
def manual_session(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        amount = data.get("amount")
        session_id = data.get("session_id")
        phone_number = data.get("phone_number")
        transaction_number = data.get("transaction_number")
        manual_session = ManualSession.objects.create(
            amount=amount,
            session_id=session_id,
            phone_number=phone_number,
            status="pending",
            transaction_number=transaction_number
        )
        print("manual_session = ",manual_session)
        manual_session.save()
        return JsonResponse({"message": "Session created successfully","session_id":manual_session.id}, status=200)
    except Exception as e:
        print(f"Error processing Manual session: {e}")
        return JsonResponse({"message": "Error processing session"}, status=500)