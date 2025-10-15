import re
import requests
from ninja import NinjaAPI,Router
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import ManualSession, WithdrawalRequest
from django.db import models
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
from users.models import ReferralBonus
from django.http import JsonResponse
from utils import generate_reference
from users.models import User
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
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
        
        # Get total bonus amount generated from sponsor change for this user
        sponsor_change_bonus_total = ReferralBonus.objects.filter(
            referrer=user,
            bonus_type='sponsor_change'
        ).aggregate(total=models.Sum('bonus_amount'))['total'] or 0
        
        # Get referral bonus amount
        referral_bonus = ReferralBonus.objects.filter(
            referrer=user,
        ).aggregate(total=models.Sum('bonus_amount'))['total'] or 0
        
        print("referral_bonus = ",referral_bonus)
        
        total_balance = (wallet.balance if wallet else 0) + referral_bonus 
        return JsonResponse({
            "balance": wallet.balance if wallet else 0,
            "referral_bonus": referral_bonus, 
            "total_balance": total_balance
        }, status=200)
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
    print("[MANUAL_SUCCESS] Manual success request")
    try:
        try:
            decoded_body = request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else str(request.body)
        except Exception as decode_err:
            print("[MANUAL_SUCCESS] Body decode error:", decode_err)
            decoded_body = str(request.body)
        print("[MANUAL_SUCCESS] Raw body:", decoded_body)
        try:
            data = json.loads(decoded_body or '{}')
        except json.JSONDecodeError as jde:
            print("[MANUAL_SUCCESS] JSON decode error:", jde)
            return JsonResponse({"error": "invalid_json", "details": str(jde)}, status=400)
        print("[MANUAL_SUCCESS] Parsed JSON:", data)
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
                # Transaction already processed - notify user if possible
                user = User.objects.filter(phone=manual_session.phone_number).first()
                try:
                    balance_text = None
                    if user:
                        wallet_obj = Wallet.objects.filter(user=user).first()
                        balance_text = f"{wallet_obj.balance} ETB" if wallet_obj else "(unknown)"
                    if user and user.telegram_id:
                        bot_token = config('BOT_TOKEN')
                        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                        message = (
                            f"⚠️ Transaction Already Processed!\n\n"
                            f"🔗 Reference: {manual_session.session_id}\n"
                            f"📊 Balance: {balance_text}\n\n"
                            f"This payment has already been credited to your wallet."
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
            print(f"DEBUG: Looking for user with phone: {manual_session.phone_number}")
            print(f"DEBUG: Manual session phone_number type: {type(manual_session.phone_number)}")

            # Resolve user: prefer manual_session.phone_number; if missing, fall back to last-4 match from payer number
            user = None
            if manual_session.phone_number:
                try:
                    user = User.objects.get(phone=manual_session.phone_number)
                    print(f"DEBUG: Found user by full phone: {user.username} (ID: {user.id})")
                except User.DoesNotExist:
                    print(f"DEBUG: No user with exact phone: {manual_session.phone_number}")
            if user is None:
                masked_payer = payer_telebirr_no or ""
                # Extract digits and take last 4
                import re
                digits = "".join(re.findall(r"\d", masked_payer))
                last4 = digits[-4:] if len(digits) >= 4 else ""
                print(f"DEBUG: Masked payer='{masked_payer}', digits='{digits}', last4='{last4}'")
                if last4:
                    candidates = list(User.objects.filter(phone__endswith=last4).values("id", "username", "phone"))
                    print(f"DEBUG: Candidates matching last4 '{last4}': {candidates}")
                    if len(candidates) == 1:
                        user = User.objects.get(id=candidates[0]["id"])  # resolve to instance
                        print(f"DEBUG: Resolved user by last4: {user.username} (ID: {user.id})")
                        # Persist phone back to session if missing
                        if not manual_session.phone_number:
                            manual_session.phone_number = user.phone
                            manual_session.save(update_fields=["phone_number"])
                    elif len(candidates) == 0:
                        return JsonResponse({"error": f"User not found by phone last4 '{last4}'"}, status=404)
                    else:
                        return JsonResponse({"error": f"Multiple users share phone last4 '{last4}'", "candidates": candidates}, status=409)
                else:
                    return JsonResponse({"error": "Unable to extract last 4 digits from payer number"}, status=400)
            
            try:
                wallet = Wallet.objects.get(user=user)
                print(f"DEBUG: Found wallet for user: {user.username}")
            except Wallet.DoesNotExist:
                print(f"DEBUG: Wallet not found for user: {user.username}")
                return JsonResponse({"error": f"Wallet not found for user: {user.username}"}, status=404)
            # Parse deposit amount
            raw_amount = details.get("amount")
            print(f"DEBUG: Telebirr raw amount value: {raw_amount} ({type(raw_amount)})")
            if isinstance(raw_amount, (int, float)):
                deposit_amount = float(raw_amount)
            else:
                from re import sub
                cleaned = sub(r"[^0-9.]", "", str(raw_amount))
                deposit_amount = float(cleaned) if cleaned else 0.0
            
            # Update manual session with correct amount
            manual_session.amount = deposit_amount
            wallet.balance += deposit_amount
            print("wallet balance = ",wallet.balance)
            wallet.save()
            manual_session.status = "success"
            manual_session.save()
            transaction = Transaction.objects.create(
                user=user,
                amount=deposit_amount,
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
                        f"💰 Amount: {deposit_amount} ETB\n"
                        f"💎 Total Credited: {deposit_amount} ETB\n"
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
            print(f"[MANUAL_SUCCESS] Non-success callback received: status={status}")
            manual_session = ManualSession.objects.filter(session_id=session_id).first()
            user = None
            if manual_session and manual_session.phone_number:
                user = User.objects.filter(phone=manual_session.phone_number).first()
            if not user:
                # Try to resolve user via payer phone last4 from details
                masked_payer = data.get("payer_telebirr_no") or details.get("payer_telebirr_no") or details.get("credited_account") or ""
                import re
                digits = "".join(re.findall(r"\d", masked_payer))
                last4 = digits[-4:] if len(digits) >= 4 else ""
                if last4:
                    candidates = list(User.objects.filter(phone__endswith=last4).values("id", "username", "phone"))
                    if len(candidates) == 1:
                        user = User.objects.get(id=candidates[0]["id"])
                        if manual_session and not manual_session.phone_number:
                            manual_session.phone_number = user.phone
                            manual_session.save(update_fields=["phone_number"]) 

            # Notify user appropriately
            msg = (data.get("message") or "Payment failed").lower()
            if user and getattr(user, 'telegram_id', None):
                try:
                    bot_token = config('BOT_TOKEN')
                    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    if "already processed" in msg:
                        text = (
                            f"⚠️ Transaction Already Processed!\n\n"
                            f"🔗 Reference: {session_id}\n"
                            f"This payment was already credited earlier."
                        )
                    else:
                        text = (
                            f"❌ Payment Failed\n\n"
                            f"🔗 Reference: {session_id}\n"
                            f"📝 Reason: {data.get('message', 'Unknown error')}"
                        )
                    requests.post(telegram_url, json={'chat_id': user.telegram_id, 'text': text, 'parse_mode': 'HTML'})
                    print(f"[MANUAL_SUCCESS] Notified user {user.telegram_id} for non-success callback")
                except Exception as notify_err:
                    print(f"[MANUAL_SUCCESS] Failed to notify user: {notify_err}")

            # Update session to failed if exists
            if manual_session:
                manual_session.status = "failed"
                manual_session.save(update_fields=["status"])
                print(f"[MANUAL_SUCCESS] Marked manual session as failed. session_id={session_id}")
            else:
                print(f"[MANUAL_SUCCESS] No manual session found for non-success callback. session_id={session_id}")
            return JsonResponse({"message": "Manual non-success processed"}, status=200)
    except Exception as e:
        import traceback
        print(f"[MANUAL_SUCCESS] Error processing Manual success: {e}")
        traceback.print_exc()
        return JsonResponse({"message": "Error processing success", "error": str(e)}, status=500)

@router.post("/manual/callback/error/")
@csrf_exempt
def manual_error(request):
    print("Manual error request")
    try:
        data = json.loads(request.body.decode('utf-8'))
        session_id = data.get("session_id")
        status = data.get("status")
        message = data.get("message", "Payment verification failed")
        manual_session = ManualSession.objects.filter(session_id=session_id).first()
        print("manual_session = ",manual_session)
        if manual_session:
            user = User.objects.filter(phone=manual_session.phone_number).first()
            if user and user.telegram_id:
                try:
                    bot_token = config('BOT_TOKEN')
                    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    error_msg = (
                        f"⚠️ Deposit Failed ⚠️\n\n"
                        f"🔗 Reference: {manual_session.session_id}\n"
                        f"❌ Reason: {message}\n\n"
                        f"Please contact support if you need assistance."
                    )
                    telegram_payload = {
                        'chat_id': user.telegram_id,
                        'text': error_msg,
                        'parse_mode': 'HTML'
                    }
                    requests.post(telegram_url, json=telegram_payload)
                    print(f"Notified user {user.telegram_id} about manual error")
                except Exception as notification_error:
                    print(f"Failed to notify user about manual error: {notification_error}")
      
        
      
        return JsonResponse({"message": "Error callback processed"}, status=200)
    except Exception as e:
        print(f"Error processing Manual error: {e}")
        return JsonResponse({"message": "Error processing error"}, status=500)    


@router.post("/manual/session/")
def manual_session(request):
    try:
        try:
            decoded_body = request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else str(request.body)
        except Exception as decode_err:
            print("[MANUAL_SESSION] Body decode error:", decode_err)
            decoded_body = str(request.body)
        print("[MANUAL_SESSION] Raw body:", decoded_body)
        try:
            data = json.loads(decoded_body or '{}')
        except json.JSONDecodeError as jde:
            print("[MANUAL_SESSION] JSON decode error:", jde)
            return JsonResponse({"error": "invalid_json", "details": str(jde)}, status=400)
        print("[MANUAL_SESSION] Parsed JSON:", data)
        amount = data.get("amount")
        session_id = data.get("session_id")
        phone_number = data.get("phone_number")
        transaction_number = data.get("transaction_number")
        print(f"[MANUAL_SESSION] amount={amount}, session_id={session_id}, phone_number={phone_number}, transaction_number={transaction_number}")
        manual_session = ManualSession.objects.create(
            amount=amount,
            session_id=session_id,
            phone_number=phone_number,
            status="pending",
            transaction_number=transaction_number
        )
        print("[MANUAL_SESSION] manual_session created:", manual_session)
        manual_session.save()
        return JsonResponse({"message": "Session created successfully","session_id":manual_session.id}, status=200)
    except Exception as e:
        import traceback
        print(f"[MANUAL_SESSION] Error processing Manual session: {e}")
        traceback.print_exc()
        return JsonResponse({"message": "Error processing session", "error": str(e)}, status=500)





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
                # Transaction already processed - notify user if possible
                user = User.objects.filter(phone=manual_session.phone_number).first()
                print("user = ",user)
                try:
                    balance_text = None
                    if user:
                        wallet_obj = Wallet.objects.filter(user=user).first()
                        balance_text = f"{wallet_obj.balance} ETB" if wallet_obj else "(unknown)"
                    if user and user.telegram_id:
                        bot_token = config('BOT_TOKEN')
                        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                        message = (
                            f"⚠️ Transaction Already Processed!\n\n"
                            f"💰 Amount: {manual_session.amount} ETB\n"
                            f"🔗 Reference: {manual_session.session_id}\n"
                            f"📊 Balance: {balance_text}\n\n"
                            f"This payment has already been credited to your wallet."
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
            print("phone from manual session = ",manual_session.phone_number)
            print(f"DEBUG: Looking for user with phone: {manual_session.phone_number}")
            print(f"DEBUG: Manual session phone_number type: {type(manual_session.phone_number)}")

            # Resolve user: prefer manual_session.phone_number; if missing, try last4 from details/credited account
            user = None
            if manual_session.phone_number:
                try:
                    user = User.objects.get(phone=manual_session.phone_number)
                    print(f"DEBUG: Found user by full phone: {user.username} (ID: {user.id})")
                except User.DoesNotExist:
                    print(f"DEBUG: No user with exact phone: {manual_session.phone_number}")
            if user is None:
                masked_payer = details.get("credited_account") or details.get("payer_telebirr_no") or ""
                import re
                digits = "".join(re.findall(r"\d", masked_payer))
                last4 = digits[-4:] if len(digits) >= 4 else ""
                print(f"DEBUG: Masked payer='{masked_payer}', digits='{digits}', last4='{last4}'")
                if last4:
                    candidates = list(User.objects.filter(phone__endswith=last4).values("id", "username", "phone"))
                    print(f"DEBUG: Candidates matching last4 '{last4}': {candidates}")
                    if len(candidates) == 1:
                        user = User.objects.get(id=candidates[0]["id"])  # resolve to instance
                        print(f"DEBUG: Resolved user by last4: {user.username} (ID: {user.id})")
                        if not manual_session.phone_number:
                            manual_session.phone_number = user.phone
                            manual_session.save(update_fields=["phone_number"])
                    elif len(candidates) == 0:
                        return JsonResponse({"error": f"User not found by phone last4 '{last4}'"}, status=404)
                    else:
                        return JsonResponse({"error": f"Multiple users share phone last4 '{last4}'", "candidates": candidates}, status=409)
                else:
                    return JsonResponse({"error": "Unable to extract last 4 digits from payer number"}, status=400)

            try:
                wallet = Wallet.objects.get(user=user)
                print(f"DEBUG: Found wallet for user: {user.username}")
            except Wallet.DoesNotExist:
                print(f"DEBUG: Wallet not found for user: {user.username}")
                return JsonResponse({"error": f"Wallet not found for user: {user.username}"}, status=404)
            
            # Parse deposit amount
            raw_amount = details.get("Transferred Amount")
            print(f"DEBUG: CBE raw amount value: {raw_amount} ({type(raw_amount)})")
            if isinstance(raw_amount, (int, float)):
                deposit_amount = float(raw_amount)
            else:
                from re import sub
                cleaned = sub(r"[^0-9.]", "", str(raw_amount))
                deposit_amount = float(cleaned) if cleaned else 0.0
            
            # Update manual session with correct amount
            manual_session.amount = deposit_amount
            wallet.balance += deposit_amount
            print("wallet balance = ",wallet.balance)
            wallet.save()
            manual_session.status = "success"
            manual_session.save()
            transaction = Transaction.objects.create(
                user=user,
                amount=deposit_amount,
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
                    message = f"🎉 Deposit Successful! 🎉\n\n💰 Amount: {deposit_amount} ETB\n💎 Total Credited: {deposit_amount} ETB\n📊 New Balance: {wallet.balance} ETB\n🔗 Reference: {manual_session.session_id}\n\n✅ Your account has been credited successfully!"
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


# Transaction Statistics API Endpoints
@router.get("/transactions/stats/")
def get_transaction_stats(request):
    """Get transaction statistics for dashboard"""
    try:
        # Get data for last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Transaction statistics
        total_deposits = Transaction.objects.filter(type="DEPOSIT", created_at__gte=thirty_days_ago).count()
        total_withdrawals = Transaction.objects.filter(type="WITHDRAW", created_at__gte=thirty_days_ago).count()
        total_withdrawals_amount = Transaction.objects.filter(type="WITHDRAW", created_at__gte=thirty_days_ago).aggregate(Sum('amount'))['amount__sum'] or 0
        total_deposits_amount = Transaction.objects.filter(type="DEPOSIT", created_at__gte=thirty_days_ago).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Wallet statistics
        total_wallet_balance = Wallet.objects.aggregate(Sum('balance'))['balance__sum'] or 0
        pending_withdrawals = WithdrawalRequest.objects.filter(status='pending').count()
        pending_withdrawals_amount = WithdrawalRequest.objects.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Calculate growth percentages (comparing with previous 30 days)
        previous_period_start = timezone.now() - timedelta(days=60)
        previous_deposits_amount = Transaction.objects.filter(type="DEPOSIT", created_at__gte=previous_period_start, created_at__lt=thirty_days_ago).aggregate(Sum('amount'))['amount__sum'] or 0
        revenue_growth = ((total_deposits_amount - previous_deposits_amount) / previous_deposits_amount * 100) if previous_deposits_amount > 0 else 0
        
        return JsonResponse({
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "total_withdrawals_amount": float(total_withdrawals_amount),
            "total_deposits_amount": float(total_deposits_amount),
            "total_wallet_balance": float(total_wallet_balance),
            "pending_withdrawals": pending_withdrawals,
            "pending_withdrawals_amount": float(pending_withdrawals_amount),
            "revenue_growth": round(revenue_growth, 1),
            "period": "last_30_days",
            "date_range": {
                "from": thirty_days_ago.strftime('%m/%d/%Y'),
                "to": timezone.now().strftime('%m/%d/%Y')
            }
        }, status=200)
    except Exception as e:
        print(f"Error getting transaction stats: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@router.get("/transactions/recent/")
def get_recent_transactions(request, limit: int = 10):
    """Get recent transactions"""
    try:
        transactions = Transaction.objects.select_related('user').order_by('-created_at')[:limit]
        
        transaction_list = []
        for transaction in transactions:
            transaction_list.append({
                "id": transaction.id,
                "user": {
                    "username": transaction.user.username,
                    "phone": transaction.user.phone,
                    "telegram_id": transaction.user.telegram_id
                },
                "amount": float(transaction.amount),
                "type": transaction.type,
                "status": transaction.status,
                "reference": transaction.reference,
                "created_at": transaction.created_at.isoformat()
            })
        
        return JsonResponse({
            "transactions": transaction_list,
            "count": len(transaction_list)
        }, status=200)
    except Exception as e:
        print(f"Error getting recent transactions: {e}")
        return JsonResponse({"error": str(e)}, status=500)


@router.get("/transactions/by-type/")
def get_transactions_by_type(request, transaction_type: str = None):
    """Get transactions filtered by type (DEPOSIT, WITHDRAW, BET, WIN)"""
    try:
        if transaction_type:
            transactions = Transaction.objects.filter(type=transaction_type).select_related('user').order_by('-created_at')
        else:
            transactions = Transaction.objects.select_related('user').order_by('-created_at')
        
        transaction_list = []
        for transaction in transactions:
            transaction_list.append({
                "id": transaction.id,
                "user": {
                    "username": transaction.user.username,
                    "phone": transaction.user.phone,
                    "telegram_id": transaction.user.telegram_id
                },
                "amount": float(transaction.amount),
                "type": transaction.type,
                "status": transaction.status,
                "reference": transaction.reference,
                "created_at": transaction.created_at.isoformat()
            })
        
        return JsonResponse({
            "transactions": transaction_list,
            "count": len(transaction_list),
            "type": transaction_type or "all"
        }, status=200)
    except Exception as e:
        print(f"Error getting transactions by type: {e}")
        return JsonResponse({"error": str(e)}, status=500)


