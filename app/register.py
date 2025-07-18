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

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    BACK_URL = get_bot_seetings().get("bot_url")
    # Check if the message contains a contact
    if update.message.contact:
        phone_number = update.message.contact.phone_number
        user_data["phone"] = phone_number

        user_id = update.message.from_user.id
        first_name = update.message.from_user.first_name,
        last_name = update.message.from_user.last_name
        confirm_password= update.message.text
        user_data.update({
            'telegram_id': str(update.message.from_user.id)
        })
        user_data.update({
            'phone': user_data.get('phone',"botphone")
        })
        
        user_data.update({
            "email":f"{user_data.get('username')}@gmail.com"
        })

        username = user_data.get("username",first_name)
        phone = user_data.get('phone',"botphone")
        password = "123456"
        user_data.update({'password':password})


        


        response = requests.post(f"{BACK_URL}/api/v1/users/register", json=user_data)

        if response.status_code == 200:  # Assume 201 means success
            await update.message.reply_text("Registration completed successfully!")
            await update.message.reply_text("Please click the button below to proceed to the next step:", reply_markup=play_options_keyboard())
        else:
            print("response = ",response.json())
            await update.message.reply_text(f"Registration failed")

      

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Registration canceled.")
    return ConversationHandler.END

