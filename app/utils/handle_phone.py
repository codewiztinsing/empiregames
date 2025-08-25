import requests
from helpers import get_bot_seetings
from register import play_options_keyboard
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import logging

logger = logging.getLogger(__name__)


async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    SERVER_URL = get_bot_seetings().get("server_url")
    logger.info(f"SERVER_URL = {SERVER_URL}")
    
    if update.message.contact:
        telegram_id = update.message.from_user.id
        logger.info(f"telegram_id = {telegram_id}")

        # Check if user already exists
        check_url = f"{SERVER_URL}/api/v1/auth/register"
        logger.info(f"Checking if user exists at: {check_url}")
        
        
        try:
            check_response = requests.get(check_url)
            logger.info(f"Check user response status: {check_response.status_code}")
            logger.info(f"Check user response text: {check_response.text}")
            
        
            # User doesn't exist, proceed with registration
            create_url = f"{SERVER_URL}/api/v1/users/"
            logger.info(f"Creating user with payload: {create_url}")
            payload = {
                "username": update.message.from_user.username or update.message.from_user.first_name,
                "telegramId": str(telegram_id),  # Convert to string as API expects
                "phoneNumber": update.message.contact.phone_number
            }
            
            logger.info(f"Creating user with payload: {payload}")
            create_response = requests.post(create_url, json=payload)
            logger.info(f"Create user response status: {create_response.status_code}")
            logger.info(f"Create user response text: {create_response.text}")
            if create_response.status_code == 201:
                data = create_response.json()
                await update.message.reply_text(data.get("message"))
                await update.message.reply_text("Please click the button below to proceed:", reply_markup=play_options_keyboard())
            else:
                data = create_response.json()
                await update.message.reply_text(data.get("error"))
                await update.message.reply_text("Please click the button below to proceed:", reply_markup=play_options_keyboard())

            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            await update.message.reply_text("Network error. Please try again later.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            await update.message.reply_text("An unexpected error occurred. Please try again later.")
    else:
        await update.message.reply_text("Please share your contact information to register.")
        return PHONE

    return ConversationHandler.END
      
