from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, ContextTypes
import requests
import os
from utils import get_bot_seetings
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
import requests
import re
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
import logging
logger = logging.getLogger(__name__)
user_data = {}  
# Define states for conversation
PHONE,EMAIL,PASSWORD,CONFIRM_PASSWORD = range(4)

async def begin_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the registration process"""
    await update.message.reply_text(
        "Welcome to registration! Please share your phone number to continue.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("Share Contact", request_contact=True)]],
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    return PHONE







def play_options_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🎮 Play 10", callback_data='10')],
        [InlineKeyboardButton("🎮 Play Demo", callback_data='play_demo')],
        [InlineKeyboardButton("🔙  Back to Menu", callback_data='back')]
    ]
    return InlineKeyboardMarkup(keyboard)







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
            
            if check_response.status_code == 200:
                # User already exists
                await update.message.reply_text("You are already registered!")
                await update.message.reply_text("Please click the button below to proceed:", reply_markup=play_options_keyboard())
                return ConversationHandler.END
            
            # User doesn't exist, proceed with registration
            create_url = f"{SERVER_URL}/api/v1/auth/register"
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
                try:
                    user_data = create_response.json()
                    logger.info(f"User created successfully: {user_data}")
                    await update.message.reply_text("Registration completed successfully!")
                    await update.message.reply_text("Please click the button below to proceed:", reply_markup=play_options_keyboard())
                except ValueError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                    await update.message.reply_text("Registration completed but there was an issue with the response. Please try again later.")
            else:
                logger.error(f"Registration failed with status {create_response.status_code}: {create_response.text}")
                await update.message.reply_text("Registration failed. Please try again later.")
                
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
      

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Registration canceled.")
    return ConversationHandler.END

