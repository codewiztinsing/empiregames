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
# Define states for conversation - must match webbot.py states
# From webbot.py: GET_DEPOSIT_AMOUNT,WITHDRAW_AMOUNT_CONFIRM,WITHDRAW_AMOUNT_CANCEL,CHOOSE_PAYMENT_METHOD,GET_WITHDRAW_ACCOUNT,GET_TRANSCATION_DETAILS,PHONE,REGISTER,SOME_STATE,WAIT_FOR_PAYMENT = range(2,12)
PHONE = 8
REGISTER = 9
SOME_STATE = 10
WAIT_FOR_PAYMENT = 11





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
    BACK_URL = get_bot_seetings().get("bot_url")
    # check user already exists
    url = f"{BACK_URL}/api/v1/users/{update.message.from_user.id}"
    user_exists = requests.get(url)
    print("user_exists = ",user_exists.json())
    telegram_id = user_exists.json().get("telegram_id",None)
    print("telegram_id = ",telegram_id)
    if telegram_id != None:
        await update.message.reply_text("You are already registered")
        return ConversationHandler.END

    # Check if the message contains a contact
    if update.message.contact:
        phone_number = update.message.contact.phone_number
        user_data["phone"] = phone_number
        print("phone_number = ",phone_number)
        user_id = update.message.from_user.id
        first_name = update.message.from_user.first_name
        last_name = update.message.from_user.last_name
        confirm_password= update.message.text
        username =  update.message.from_user.username or generate_random_username()
        user_data.update({
            'telegram_id': str(update.message.from_user.id),
            'phone': phone_number
        })
        # Check if user came from a referral link
        referrer_id = context.user_data.get('referrer_id')
        if referrer_id:
            # User came from referral link, automatically use the referrer ID
            await update.message.reply_text(
                f"🎉 You were referred by someone! Using referral ID: {referrer_id}\n"
                "Proceeding with registration..."
            )
            # Skip to referral code handling with the referrer ID
            return await handle_referral_code_from_link(update, context, referrer_id)
        else:
            # No referral link, proceed with registration without referral code
            await update.message.reply_text("Proceeding with registration...")
            return await complete_registration_without_referral(update, context)

async def complete_registration_without_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Complete registration without any referral code"""
    BACK_URL = get_bot_seetings().get("bot_url")
    # username from telegrm profile,if not use first nam
    username = update.message.from_user.username or update.message.from_user.first_name
    
    
    # Prepare user data for registration
    user_data.update({
        'phone': user_data.get('phone',"botphone"),
        'username': username,
        'password': user_data.get('password',"123456"),
        'email': user_data.get('email',f"{username}@gmail.com"),
        'referral_code': None  # No referral code
    })
    
    print("user_data = ",user_data)
    response = requests.post(f"{BACK_URL}/api/v1/users/register", json=user_data)
    
    if response.status_code == 200:
        response_data = response.json()
        success_message = "Registration completed successfully!"
        
        await update.message.reply_text(success_message)
        await update.message.reply_text("please user /start to start playing")
    else:
        print(f"Registration failed: {response.json()}")
        error_message = response.json().get('message', 'Registration failed')
        await update.message.reply_text(f"Registration failed: {error_message}")
    
    return ConversationHandler.END

async def handle_referral_code_from_link(update: Update, context: ContextTypes.DEFAULT_TYPE, referrer_id: int):
    """Handle referral code when user comes from a referral link"""
    BACK_URL = get_bot_seetings().get("bot_url")
    
    # Get the referrer's referral code from the API
    try:
        referrer_response = requests.get(f"{BACK_URL}/api/v1/users/{referrer_id}")
        if referrer_response.status_code == 200:
            referrer_data = referrer_response.json()
            if referrer_data.get('success', False):
                referral_code = referrer_data.get('referral_code')
                if referral_code:
                    await update.message.reply_text(f"Using referrer's code: {referral_code}")
                else:
                    await update.message.reply_text("Referrer not found or has no referral code. Continuing without referral...")
                    referral_code = None
            else:
                await update.message.reply_text("Referrer not found. Continuing without referral...")
                referral_code = None
        else:
            await update.message.reply_text("Error checking referrer. Continuing without referral...")
            referral_code = None
    except Exception as e:
        print(f"Error getting referrer data: {e}")
        await update.message.reply_text("Error checking referrer. Continuing without referral...")
        referral_code = None
    
    # Prepare user data for registration
    username = user_data.get('username', f"user_{random.randint(1000,9999)}")
    user_data.update({
        'phone': user_data.get('phone',"botphone"),
        'username': username,
        'password': user_data.get('password',"123456"),
        'email': user_data.get('email',f"{username}@gmail.com"),
        'referral_code': referral_code
    })
    
    print("user_data = ",user_data)
    response = requests.post(f"{BACK_URL}/api/v1/users/register", json=user_data)
    
    if response.status_code == 200:
        response_data = response.json()
        success_message = "Registration completed successfully!"
        
        # Add referral bonus information if applicable
        if response_data.get('referral_bonus', 0) > 0:
            success_message += f"\n🎉 You received {response_data['referral_bonus']} ETB referral bonus!"
        
        await update.message.reply_text(success_message)
        await update.message.reply_text("Please click the button below to proceed to the next step:", reply_markup=play_options_keyboard())
    else:
        print(f"Registration failed: {response.json()}")
        error_message = response.json().get('message', 'Registration failed')
        await update.message.reply_text(f"Registration failed: {error_message}")
    
    return ConversationHandler.END

# handle_referral_code function removed - no longer needed since we don't ask for manual referral codes

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Registration canceled.")
    return ConversationHandler.END

