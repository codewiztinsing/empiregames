from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, ContextTypes
import requests
import os
import random
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

user_data = {}  
# Define states for conversation
PHONE,EMAIL,PASSWORD,CONFIRM_PASSWORD = range(4)





def play_options_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🎮 Play 10", callback_data='10'),
         InlineKeyboardButton("🎮 Play 20", callback_data='20')],
        [InlineKeyboardButton("🎮 Play 50", callback_data='50'),
         InlineKeyboardButton("🎮 Play 100", callback_data='100')],
        [InlineKeyboardButton("🎮 Play Demo", callback_data='play_demo'),
         InlineKeyboardButton("🔙  Back to Menu", callback_data='back')
         ],
    ]
    return InlineKeyboardMarkup(keyboard)





async def begin_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    BACK_URL = get_bot_seetings().get("bot_url")
    telegram_id = update.message.from_user.id
    username = update.message.from_user.username if update.message.from_user.username else update.message.from_user.first_name
    user_data["username"] = username



    url  = f"{BACK_URL}/api/v1/users/{telegram_id}/"
    user_exists  = requests.get(url)
    if user_exists.status_code == 200:
        user_exists = user_exists.json()
        
        await update.message.reply_text(
                    text="You are already registred,please start playing:",
                    reply_markup=play_options_keyboard()
                )
    else:
        await update.message.reply_text(f"Welcome! Your username is: {username}. Please share your phone number.")
        referrer_id = context.user_data.get('referrer_id')
     
        # Create a button to share phone number
        phone_button = KeyboardButton("Share Phone Number", request_contact=True)
    
    
        reply_markup = ReplyKeyboardMarkup([[phone_button]], resize_keyboard=True, one_time_keyboard=True)

        await update.message.reply_text("Click the button below to share your phone number:", reply_markup=reply_markup)

        return PHONE  # Move to the PHONE state

def generate_random_username():
    return f"user_{random.randint(1000,9999)}"

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("DEBUG: handle_phone function called")
    BACK_URL = get_bot_seetings().get("bot_url")
    
    # Check if user already exists
    url = f"{BACK_URL}/api/v1/users/{update.message.from_user.id}"
    try:
        user_exists = requests.get(url)
        print("user_exists = ", user_exists.json())
        telegram_id = user_exists.json().get("telegram_id", None)
        print("telegram_id = ", telegram_id)
        if telegram_id is not None:
            await update.message.reply_text("You are already registered!")
            return ConversationHandler.END
    except Exception as e:
        print(f"Error checking user existence: {e}")

    # Check if the message contains a contact
    print("DEBUG: Checking for contact in message")
    print(f"DEBUG: Message type: {type(update.message)}")
    print(f"DEBUG: Message content: {update.message}")
    if update.message.contact:
        print("DEBUG: Contact found in message")
        phone_number = update.message.contact.phone_number
        print("phone_number = ", phone_number)
        
        user_id = update.message.from_user.id
        first_name = update.message.from_user.first_name
        last_name = update.message.from_user.last_name
        username = update.message.from_user.username or generate_random_username()
        
        # Get referrer_id from context if available
        referrer_id = context.user_data.get('referrer_id')
        
        # Prepare user data for registration
        user_data = {
            'telegram_id': str(user_id),
            'phone': phone_number,
            'username': username,
            'password': "123456",  # Default password
            'email': f"{username}@gmail.com",
            'first_name': first_name or "",
            'last_name': last_name or ""
        }
        
        # Add referred_by (telegram_id of referrer) if user came through referral
        if referrer_id:
            user_data['referred_by'] = str(referrer_id)
            print(f"Registering user with referred_by: {referrer_id}")
        
        print("user_data = ", user_data)
        
        try:
            response = requests.post(f"{BACK_URL}/api/v1/users/register", json=user_data)
            if response.status_code == 200 or response.status_code == 201:
                await update.message.reply_text("Registration completed successfully!")
                # If user came through referral, show special message
                if referrer_id:
                    await update.message.reply_text(f"🎉 Welcome! You were referred by user {referrer_id}")
                
                await update.message.reply_text("Please use /play to start playing.")
                return ConversationHandler.END
            else:
                print(f"Registration failed: {response.json()}")
                error_message = response.json().get('message', 'Registration failed. Please try again.')
                await update.message.reply_text(error_message)
                return ConversationHandler.END
        except Exception as e:
            print(f"Error during registration: {e}")
            await update.message.reply_text("Registration failed. Please try again later.")
            return ConversationHandler.END
    else:
        await update.message.reply_text("Please share your phone number using the button below.")
        return REGISTER

      

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Registration canceled.")
    return ConversationHandler.END

