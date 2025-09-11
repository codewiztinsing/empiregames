import requests
import uuid
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.bot_settings import get_bot_seetings
from utils.bot_settings import initialize_manual_session
from decouple import config

async def handle_manual_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    manual_payment_method = context.user_data['payment_method']
    manual_payment_url = config("MANUAL_BASE_URL")
    manual_payment_url = manual_payment_url + "receipts/verify/"
    data = {
        "message": update.message.text,
        "paymentMethod": manual_payment_method,
        "session_id": context.user_data['session_id']
    }
    response = requests.post(manual_payment_url, json=data)
    await update.message.reply_text(f"Payment method: {manual_payment_method}")
    