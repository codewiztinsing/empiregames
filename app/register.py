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
        # Handle referred_by field - convert telegram_id to User instance
        referred_by_user = None
        if user_data.get('referred_by'):
            try:
                referred_by_user = User.objects.get(telegram_id=user_data['referred_by'])
                print(f"DEBUG: Found referrer user: {referred_by_user.username} (ID: {referred_by_user.id})")
                
                # Check if referrer has deposit transaction history
                from wallet.models import Transaction
                referrer_deposits = Transaction.objects.filter(
                    wallet__user=referred_by_user,
                    type='DEPOSIT',
                    status='success'
                ).exists()
                
                if not referrer_deposits:
                    print(f"❌ ERROR: Referrer {referred_by_user.username} has no deposit history - blocking registration")
                    return None
                else:
                    print(f"✅ Referrer {referred_by_user.username} has deposit history - allowing registration")
                    
            except User.DoesNotExist:
                print(f"DEBUG: Referrer with telegram_id {user_data['referred_by']} not found")
                return None
        
        user = User.objects.create(
            telegram_id=user_data['telegram_id'],
            phone=user_data['phone'],
            username=user_data['username'],
            password=user_data['password'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            referred_by=referred_by_user
        )
        
        # Wallet is automatically created by Django signals, so we don't need to create it manually
        # Just get the wallet to ensure it exists
        wallet = Wallet.objects.get(user=user)
        
        # If user was referred, add 5 birr to referrer's balance
        print(f"DEBUG: Checking referral bonus for user_data: {user_data}")
        print(f"DEBUG: referred_by value: {user_data.get('referred_by')}")
        
        if user_data.get('referred_by') and referred_by_user:
            print(f"DEBUG: User was referred by: {user_data['referred_by']}")
            try:
                referrer_telegram_id = user_data['referred_by']
                print(f"DEBUG: Using already found referrer: {referred_by_user.username} (ID: {referred_by_user.id})")
                
                referrer_wallet = Wallet.objects.get(user=referred_by_user)
                print(f"DEBUG: Found referrer wallet. Current balance: {referrer_wallet.balance}")
                
                # Add 5 birr to referrer's balance
                old_balance = referrer_wallet.balance
                referrer_wallet.balance += 5.0
                referrer_wallet.save()
                
                print(f"DEBUG: Updated referrer balance from {old_balance} to {referrer_wallet.balance}")
                print(f"✅ SUCCESS: Added 5 birr referral bonus to user {referrer_telegram_id}")
                print(f"🎉 Referral Bonus: User {referrer_telegram_id} received 5 ETB for referring {user.first_name or user.username}")
                
            except Wallet.DoesNotExist:
                print(f"❌ ERROR: Wallet for referrer {user_data['referred_by']} not found")
            except Exception as e:
                print(f"❌ ERROR: Error adding referral bonus: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("DEBUG: No referred_by found in user_data or referrer user not found, skipping referral bonus")
        
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
    print(f"DEBUG: begin_register called with context.user_data: {context.user_data}")
    telegram_id = update.message.from_user.id
    username = update.message.from_user.username if update.message.from_user.username else update.message.from_user.first_name
    user_data["username"] = username

    # Check if user exists using Django ORM
    user = await check_user_exists(telegram_id)
    if user:
        print(f"DEBUG: User {telegram_id} already exists")
        await update.message.reply_text(
                    text="You are already registred,please start playing:",
                    reply_markup=play_options_keyboard()
                )
    else:
        print(f"DEBUG: User {telegram_id} does not exist, starting registration")
        await update.message.reply_text(f"Welcome! Your username is: {username}. Please share your phone number.")
        referrer_id = context.user_data.get('referrer_id')
        print(f"DEBUG: begin_register - referrer_id from context: {referrer_id}")
     
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
        print(f"DEBUG: handle_phone - context.user_data: {context.user_data}")
        print(f"DEBUG: handle_phone - referrer_id from context: {referrer_id}")
        
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
        print(f"DEBUG: Registration process - referrer_id from context: {referrer_id}")
        if referrer_id:
            user_data['referred_by'] = str(referrer_id)
            print(f"DEBUG: Setting referred_by to: {user_data['referred_by']}")
            print(f"Registering user with referred_by: {referrer_id}")
        else:
            print("DEBUG: No referrer_id found in context")
        
        print("DEBUG: Final user_data = ", user_data)
        
        try:
            # Create user using Django ORM
            user = await create_user(user_data)
            if user:
                await update.message.reply_text("Registration completed successfully!")
                # If user came through referral, show special message
                if referrer_id:
                    await update.message.reply_text(f"🎉 Welcome! You were referred by user {referrer_id}")
                    await update.message.reply_text("Your referrer has received 5 ETB bonus for referring you!")
                
                await update.message.reply_text("Please use /play to start playing.")
                return ConversationHandler.END
            else:
                # Check if registration failed due to invalid referrer
                if referrer_id:
                    await update.message.reply_text("❌ Registration failed!")
                    await update.message.reply_text("This referral link is not eligible. The referrer has not made any deposits.")
                    await update.message.reply_text("Please register without a referral link or use a different referral link.")
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

@sync_to_async
def is_referrer_eligible(telegram_id):
    """Check if a referrer is eligible (has made deposits)"""
    try:
        from wallet.models import Transaction
        referrer = User.objects.get(telegram_id=telegram_id)
        has_deposits = Transaction.objects.filter(
            wallet__user=referrer,
            type='DEPOSIT',
            status='success'
        ).exists()
        return has_deposits
    except User.DoesNotExist:
        return False
    except Exception as e:
        print(f"Error checking referrer eligibility: {e}")
        return False

