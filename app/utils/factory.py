import requests
import uuid
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.bot_settings import get_bot_seetings
from utils.bot_settings import initialize_manual_session,verify_telebirr_receipt,verify_cbe_receipt
from utils.helpers import get_user_phone
from decouple import config

async def handle_manual_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    manual_payment_method = context.user_data['payment_method']
    manual_payment_url = config("MANUAL_BASE_URL")
    MANUAL_API_KEY = config("MANUAL_API_KEY")
    
    
    # Debug: Log all user_data keys to understand what's available
    print(f"DEBUG: User data keys: {list(context.user_data.keys())}")
    print(f"DEBUG: Deposit amount: {context.user_data.get('deposit_amount', 'NOT FOUND')}")
    print(f"DEBUG: Payment method: {manual_payment_method}")
    if manual_payment_method == "manual_telebirr":
        manual_payment_url = manual_payment_url + "receipts/verify/telebirr/"
        callbackurl = config("BACK_URL") + "/api/v1/wallet/manual/callback/success/"
        errorUrl    = config("BACK_URL") + "/api/v1/wallet/manual/callback/error/"
    elif manual_payment_method == "manual_cbe":
        manual_payment_url = manual_payment_url + "receipts/verify/cbe/"
        callbackurl = config("BACK_URL") + "/api/v1/wallet/manual/callback/cbe/success/"
        errorUrl    = config("BACK_URL") + "/api/v1/wallet/manual/callback/cbe/error/"
  
    data = {
        "message": update.message.text,
        "callbackurl": callbackurl,
        "errorUrl": errorUrl
        
    }
    print("data = ",data)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": MANUAL_API_KEY
    }
    response = requests.post(manual_payment_url, json=data, headers=headers)
    if response.status_code in [202,200]:
        # Get deposit amount from user_data, default to 0 and proceed
        amount = context.user_data.get('deposit_amount', 0)
        
        session_id = response.json().get("session_id")
        phone_number = get_user_phone(update.effective_user.id)
        if manual_payment_method == "manual_telebirr":
            # Initialize with 0 amount, callback will update with correct amount
            initialize_manual_session(0, session_id, phone_number)
            verify_telebirr_receipt(message,session_id)
        elif manual_payment_method == "manual_cbe":
            # Initialize with 0 amount, callback will update with correct amount
            initialize_manual_session(0, session_id, phone_number)
            verify_cbe_receipt(message,session_id)
    
        await update.message.reply_text(f"Session created successfully, please wait for the payment to be verified")
        return ConversationHandler.END
    else:
        print("response xxxx= ",response.status_code)
        await update.message.reply_text(f"Failed to create session, please try again")
        return ConversationHandler.END
    


