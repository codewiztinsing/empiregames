from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, ContextTypes
import os
import random
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
import re
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
import django
from django.conf import settings
from asgiref.sync import sync_to_async

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import Django models
from users.models import User
from wallet.models import Wallet

# Django ORM async functions
@sync_to_async
def check_user_exists(telegram_id):
    """Check if user exists by telegram_id"""
    try:
        user = User.objects.get(telegram_id=telegram_id)
        return user
    except User.DoesNotExist:
        return None

@sync_to_async
def create_user(user_data):
    """Create a new user using Django ORM"""
    try:
        user = User.objects.create(
            telegram_id=user_data['telegram_id'],
            phone=user_data['phone'],
            username=user_data['username'],
            password=user_data['password'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            referred_by=user_data.get('referred_by')
        )
        
        # Wallet is automatically created by Django signals, so we don't need to create it manually
        # Just get the wallet to ensure it exists
        wallet = Wallet.objects.get(user=user)
        
        return user
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

@sync_to_async
def get_user_by_telegram_id(telegram_id):
    """Get user by telegram_id"""
    try:
        return User.objects.get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return None

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
    telegram_id = update.message.from_user.id
    username = update.message.from_user.username if update.message.from_user.username else update.message.from_user.first_name
    user_data["username"] = username

    # Check if user exists using Django ORM
    user = await check_user_exists(telegram_id)
    if user:
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
    
    # Check if user already exists using Django ORM
    telegram_id = update.message.from_user.id
    try:
        user = await get_user_by_telegram_id(telegram_id)
        if user:
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
            # Create user using Django ORM
            user = await create_user(user_data)
            if user:
                await update.message.reply_text("Registration completed successfully!")
                # If user came through referral, show special message
                if referrer_id:
                    await update.message.reply_text(f"🎉 Welcome! You were referred by user {referrer_id}")
                    await update.message.reply_text("You've received 10 ETB in referral earnings for being referred!")
                
                await update.message.reply_text("Please use /play to start playing.")
                return ConversationHandler.END
            else:
                await update.message.reply_text("Registration failed. Please try again.")
                return ConversationHandler.END
        except Exception as e:
            print(f"Error during registration: {e}")
            await update.message.reply_text("Registration failed. Please try again later.")
            return ConversationHandler.END
    else:
        await update.message.reply_text("Please share your phone number using the button below.")
        return PHONE

      

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Registration canceled.")
    return ConversationHandler.END

