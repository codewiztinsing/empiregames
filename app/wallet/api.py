import re
import requests
from ninja import NinjaAPI,Router
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import ManualSession, WithdrawalRequest
from decouple import config
from .schema import (ChapaSessionSchema,
    ChapaSessionResponseSchema, 
    ChapaCallbackSchema,
    WalletSchema, 
    AddisPaySessionSchema,
    AddisPaySessionResponseSchema,
    AddisPayCallbackSchema
 )
from .models import ChapaSession, Wallet,Transaction, AddisPaySession, PaymentDepositGatewaySettings, PaymentWithdrawalGatewaySettings
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
        session_id = data.get("session_id")
        status = data.get("status")
        # Extract payer number from either top-level or nested 'data'
        details = data.get("data") or {}
        transaction_number = details.get("transaction_number")
        payer_telebirr_no = data.get("payer_telebirr_no") or details.get("payer_telebirr_no") or details.get("credited_account")
        print("payer_telebirr_no = ", payer_telebirr_no)
        if not payer_telebirr_no:
            return JsonResponse({"message": "Missing payer_telebirr_no"}, status=400)

        if status == "success":
            manual_session = ManualSession.objects.filter(session_id=session_id).first()
            if not manual_session:
                print("No manual session found for session id:", session_id)
                return JsonResponse({"message": "No matching session found"}, status=404)
                        
            if manual_session.status == "success":
                # Transaction already processed
                user = User.objects.filter(phone=manual_session.phone_number).first()
                if user and user.telegram_id:
                    try:
                        bot_token = config('BOT_TOKEN')
                        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                        message = (
                            f"🎉 Deposit Failed! 🎉\n\n"
                            f"📊 New Balance: {wallet.balance} ETB\n"
                            f"🔗 Reference: {manual_session.session_id}\n\n"
                            f"❌ Your account has been credited failed!"
                        )
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
            wallet.balance += float(details.get("amount"))
            print("wallet balance = ",wallet.balance)
            wallet.save()
            manual_session.status = "success"
            manual_session.save()
            transaction = Transaction.objects.create(
                user=user,
                amount=float(details.get("amount")),
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
                    message = (
                        f"🎉 Deposit Successful! 🎉\n\n"
                        f"💰 Amount: {details.get('amount')} ETB\n"
                        f"📊 New Balance: {wallet.balance} ETB\n"
                        f"🔗 Reference: {manual_session.session_id}\n\n"
                        f"✅ Your account has been credited successfully!"
                    )
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





@router.post("/manual/callback/cbe/success/")
@csrf_exempt
def manual_cbe_success(request):
    print("Manual success request")
    try:
        data = json.loads(request.body.decode('utf-8'))
        session_id = data.get("session_id")
        status = data.get("status")
        # Extract payer number from either top-level or nested 'data'
        details = data.get("data") or {}
        transaction_number = details.get("transaction_number")
        customerName = data.get("Customer Name") or details.get("Customer Name") or details.get("credited_account")
        if not customerName:
            return JsonResponse({"message": "Missing customerName"}, status=400)

        if status == "success":
            manual_session = ManualSession.objects.filter(session_id=session_id).first()
            if not manual_session:
                print("No manual session found for session id:", session_id)
                return JsonResponse({"message": "No matching session found"}, status=404)
                        
            if manual_session.status == "success":
                # Transaction already processed
                user = User.objects.filter(phone=manual_session.phone_number).first()
                print("user = ",user)
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
            print("phone from manual session = ",manual_session.phone_number)
            user = get_object_or_404(User, phone=manual_session.phone_number)
            wallet = get_object_or_404(Wallet, user=user)
            wallet.balance += float(details.get("Transferred Amount"))
            print("wallet balance = ",wallet.balance)
            wallet.save()
            manual_session.status = "success"
            manual_session.save()
            transaction = Transaction.objects.create(
                user=user,
                amount=float(details.get("Transferred Amount")),
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
                    message = f"🎉 Deposit Successful! 🎉\n\n💰 Amount: {details.get('Transferred Amount').strip('ETB')} ETB\n📊 New Balance: {wallet.balance} ETB\n🔗 Reference: {manual_session.session_id}\n\n✅ Your account has been credited successfully!"
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


@router.post("/manual-deposit/")
def manual_deposit(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        phone = data.get('phone')
        amount = data.get('amount')
        reference = data.get('reference')
        notes = data.get('notes', '')
        
        # Validate required fields
        if not phone or not amount or not reference:
            return JsonResponse({"success": False, "message": "Phone, amount, and reference are required"}, status=400)
        
        # Find user by phone number
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "User with this phone number not found"}, status=404)
        
        # Get or create wallet
        wallet, created = Wallet.objects.get_or_create(user=user, defaults={'balance': 0})
        
        # Create manual session
        manual_session = ManualSession.objects.create(
            phone_number=phone,
            amount=amount,
            session_id=reference,
            status='success',  # Mark as successful since it's manually added
            transaction_number=reference
        )
        
        # Update wallet balance
        wallet.balance += float(amount)
        wallet.save()
        
        # Create transaction record
        transaction = Transaction.objects.create(
            user=user,
            amount=float(amount),
            type='DEPOSIT',
            status='success',
            reference=reference
        )
        
        # Notify user about successful deposit
        if user.telegram_id:
            try:
                bot_token = config('BOT_TOKEN')
                telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                message = (
                    f"🎉 Manual Deposit Added! 🎉\n\n"
                    f"💰 Amount: {amount} ETB\n"
                    f"📊 New Balance: {wallet.balance} ETB\n"
                    f"🔗 Reference: {reference}\n"
                    f"📝 Notes: {notes}\n\n"
                    f"✅ Your account has been credited by admin!"
                )
                telegram_payload = {
                    'chat_id': user.telegram_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                requests.post(telegram_url, json=telegram_payload)
                print(f"Notified user {user.telegram_id} about manual deposit")
            except Exception as notification_error:
                print(f"Failed to notify user about manual deposit: {notification_error}")
        
        return JsonResponse({
            "success": True, 
            "message": "Manual deposit added successfully",
            "transaction_id": transaction.id,
            "new_balance": wallet.balance
        }, status=200)
        
    except Exception as e:
        print(f"Error processing manual deposit: {e}")
        return JsonResponse({"success": False, "message": "Error processing manual deposit"}, status=500)

@router.post("/withdrawal/request/")
def withdrawal_request(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        amount = data.get("amount")
        user = User.objects.filter(telegram_id=data.get("telegram_id")).first()
        withdrawal_request = WithdrawalRequest.objects.create(user=user,amount=amount,status="pending")
        return JsonResponse({"message": "Withdrawal request created successfully"}, status=200)
    except Exception as e:
        print(f"Error processing Withdrawal request: {e}")
        return JsonResponse({"message": "Error processing withdrawal request"}, status=500)


@router.put("/save-payment-deposit-gateway-settings/")
def save_payment_deposit_gateway_settings(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        minimumDepositAmount = data.get("minimumDepositAmount")
        payment_deposit_gateway_settings = PaymentDepositGatewaySettings.objects.update(minimumDepositAmount=minimumDepositAmount)
        return JsonResponse({"message": "Payment deposit gateway settings saved successfully"}, status=200)
    except Exception as e:
        print(f"Error processing Payment deposit gateway settings: {e}")
        return JsonResponse({"message": "Error processing payment deposit gateway settings"}, status=500)


@router.put("/save-payment-withdrawal-gateway-settings/")
def save_payment_withdrawal_gateway_settings(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        minimumWithdrawalAmount = data.get("minimumWithdrawalAmount")
        withdrawalFee = data.get("withdrawalFee")
        payment_withdrawal_gateway_settings = PaymentWithdrawalGatewaySettings.objects.update(minimumWithdrawalAmount=minimumWithdrawalAmount, withdrawalFee=withdrawalFee)
        return JsonResponse({"message": "Payment withdrawal gateway settings saved successfully"}, status=200)
    except Exception as e:
        print(f"Error processing Payment withdrawal gateway settings: {e}")
        return JsonResponse({"message": "Error processing payment withdrawal gateway settings"}, status=500)

@router.get("/manual/deposits/settings/")
def get_manual_deposits_settings(request):
    try:
        payment_deposit_gateway_settings = PaymentDepositGatewaySettings.objects.first()
        if payment_deposit_gateway_settings:
            return JsonResponse({
                "message": "Payment deposit gateway settings retrieved successfully",
                "minimum_deposit_amount": payment_deposit_gateway_settings.minimumDepositAmount
            }, status=200)
        else:
            return JsonResponse({"message": "Payment deposit gateway settings not found"}, status=404)
    except Exception as e:
        print(f"Error processing Payment deposit gateway settings: {e}")
        return JsonResponse({"message": "Error processing payment deposit gateway settings"}, status=500)
    
@router.get("/manual/withdrawals/settings/")
def get_manual_withdrawals_settings(request):
    try:
        payment_withdrawal_gateway_settings = PaymentWithdrawalGatewaySettings.objects.first()
        if payment_withdrawal_gateway_settings:
            return JsonResponse({
                "message": "Payment withdrawal gateway settings retrieved successfully",
                "minimum_withdrawal_amount": payment_withdrawal_gateway_settings.minimumWithdrawalAmount,
                "withdrawal_fee": payment_withdrawal_gateway_settings.withdrawalFee
            }, status=200)
        else:
            return JsonResponse({"message": "Payment withdrawal gateway settings not found"}, status=404)
    except Exception as e:
        print(f"Error processing Payment withdrawal gateway settings: {e}")
        return JsonResponse({"message": "Error processing payment withdrawal gateway settings"}, status=500)


