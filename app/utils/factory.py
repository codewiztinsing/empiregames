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
    if manual_payment_method == "manual_telebirr":
        manual_payment_url = manual_payment_url + "receipts/verify/telebirr/"
    elif manual_payment_method == "manual_cbe":
        manual_payment_url = manual_payment_url + "receipts/verify/cbe/"
    callbackurl = config("BACK_URL") + "/api/v1/wallet/manual/callback/success/"
    # callbackurl = "https://webhook.site/61a691dd-df42-46b3-a4d5-f417a4d49b9d"
    errorUrl    = config("BACK_URL") + "/api/v1/wallet/manual/callback/error/"
    # errorUrl = "https://webhook.site/eb5edb76-4b62-4400-9c67-fcdc7d5bc018"
    data = {
        "message": update.message.text,
        "callbackurl": callbackurl,
        "errorUrl": errorUrl
        
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": MANUAL_API_KEY
    }
    response = requests.post(manual_payment_url, json=data, headers=headers)
    if response.status_code in [202,200]:
        amount = context.user_data['deposit_amount']
        session_id = response.json().get("session_id")
        phone_number = get_user_phone(update.effective_user.id)
        if manual_payment_method == "manual_telebirr":
            initialize_manual_session(amount, session_id, phone_number)
            verify_telebirr_receipt(message,session_id)
        elif manual_payment_method == "manual_cbe":
            initialize_manual_session(amount, session_id, phone_number)
            verify_cbe_receipt(message,session_id)
    
        await update.message.reply_text(f"Session created successfully, please wait for the payment to be verified")
        return ConversationHandler.END
    else:
        print("response xxxx= ",response.status_code)
        await update.message.reply_text(f"Failed to create session, please try again")
        return ConversationHandler.END
    


