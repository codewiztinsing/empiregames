import json
import requests
import logging
import random
import string
import os
import django
from telegram.constants import ParseMode
from decouple import config
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from datetime import datetime, timedelta
from decimal import Decimal
# Removed payment gateway integrations; keep only needed utils
from utils import get_bot_seetings, get_user_phone, leaderboard_command
# Removed Chapa/AddisPay integrations
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler,
)
from utils.helpers import daily_withdraw_limit,numnber_of_game_played,number_of_game_won,is_deposited_player,get_game_type,get_user_by_telegram_id,get_user_wallet,update_wallet_balance,create_transaction,get_user_transactions,create_withdrawal_request,get_user_withdrawal_requests,get_payment_settings,get_user_wallet_with_referrals,trigger_withdrawal_processing,trigger_withdrawal_validation,trigger_withdrawal_notification,trigger_limit_check,get_user_game_statistics
from asgiref.sync import sync_to_async
from django.conf import settings as dj_settings
from django.utils import timezone

# Ensure Django is configured when running this script directly
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from users.models import User
from wallet.models import Wallet, WithdrawalRequest, PaymentSettings, Transaction
from utils.factory import handle_manual_payment
from datetime import datetime
from telegram import BotCommand
from register import *

# Language selection states
LANGUAGE_SELECTION = 0

# Global user data storage for language preferences
user_data = {}

# Language texts
LANGUAGE_TEXTS = {
    'en': {
        'welcome': 'Welcome to Liyu Bingo!',
        'select_language': 'Please select your language:',
        'play': '🎮 Play',
        'register': '📝 Register',
        'check_balance': '💰 Check Balance',
        'deposit': '💳 Deposit',
        'contact_support': '📞 Contact Support',
        'instructions': '📚 Instructions',
        'leaderboard': '🏆 Leaderboard',
        'english': '🇺🇸 English',
        'amharic': '🇪🇹 Amharic',
        'oromo': '🇪🇹 Oromo',
        'somali': '🇸🇴 Somali',
        'tigrinya': '🇪🇹 Tigrinya',
        'user_not_found': 'User not found. Please register first.',
        'bonus_earned': '🎉 Congratulations! You\'ve earned a bonus!\n\n💰 Bonus Amount: {amount:.2f} ETB\n🎮 Consecutive Games: {games}\n\nYour bonus has been added to your wallet. Keep playing to earn more bonuses!',
        'bonus_progress': '📊 Consecutive Games Bonus Progress\n\n🎮 Games Bet: {current}/10\n🎯 Games Needed: {needed}\n\nBet {needed} more consecutive game(s) to earn a 20 ETB bonus!',
        'error_occurred': 'An error occurred. Please try again later.'
    },
    'am': {
        'welcome': 'ወደ ሊዩ ቢንጎ እንኳን ደህና መጡ!',
        'select_language': 'እባክዎ ቋንቋዎን ይምረጡ:',
        'play': '🎮 ተጫውት',
        'register': '📝 ይመዝገቡ',
        'check_balance': '💰 ሚዛን ይፈትሹ',
        'deposit': '💳 ገንዘብ ያስገቡ',
        'contact_support': '📞 ድጋፍ ያግኙ',
        'instructions': '📚 መመሪያዎች',
        'leaderboard': '🏆 አሸናፊዎች',
        'english': '🇺🇸 English',
        'amharic': '🇪🇹 አማርኛ',
        'oromo': '🇪🇹 Oromo',
        'somali': '🇸🇴 Somali',
        'tigrinya': '🇪🇹 Tigrinya',
        'user_not_found': 'ተጠቃሚ አልተገኘም። እባክዎ በመጀመሪያ ይመዝገቡ።',
        'bonus_earned': '🎉 እንኳን ደስ አለህ! ጉርሻ አግኝተሃል!\n\n💰 የጉርሻ መጠን: {amount:.2f} ብር\n🎮 ተከታታይ ጨዋታዎች: {games}\n\nጉርሻዎ ወደ የገንዘብ ቦርሳዎ ተጨመረ። ተጨማሪ ጉርሻዎችን ለማግኘት መጫወት ይቀጥሉ!',
        'bonus_progress': '📊 ተከታታይ ጨዋታዎች ጉርሻ ሂደት\n\n🎮 የተጫወቱ ጨዋታዎች: {current}/10\n🎯 የሚያስፈልጉ ጨዋታዎች: {needed}\n\n20 ብር ጉርሻ ለማግኘት {needed} ተጨማሪ ተከታታይ ጨዋታ(ዎች) ይጫወቱ!',
        'error_occurred': 'ስህተት ተፈጥሯል። እባክዎ ቆይተው ይሞክሩ።'
    },
    'om': {
        'welcome': 'Liyu Bingo irratti baga nagaan dhufte!',
        'select_language': 'Maaloo afaan kee filadhu:',
        'play': '🎮 Taphadhu',
        'register': '📝 Galmaa\'i',
        'check_balance': '💰 Balansi mirkaneessi',
        'deposit': '💳 Qarshii galchi',
        'contact_support': '📞 Deeggarsa argadhu',
        'instructions': '📚 Qajeelchii',
        'leaderboard': '🏆 Abbaa Duulaa',
        'english': '🇺🇸 English',
        'amharic': '🇪🇹 Amharic',
        'oromo': '🇪🇹 Afaan Oromoo',
        'somali': '🇸🇴 Somali',
        'tigrinya': '🇪🇹 Tigrinya',
        'user_not_found': 'Fayyadamaa hin argamne. Maaloo jalqaba galma\'i.',
        'bonus_earned': '🎉 Bagaan gahe! Bonas argatte!\n\n💰 Gatii Bonas: {amount:.2f} ETB\n🎮 Tapha Walitti Fufan: {games}\n\nBonas kee wallet kee keessatti dabalamuun isaa. Bonas dabalataa argachuuf tapha itti fufi!',
        'bonus_progress': '📊 Tapha Walitti Fufan Bonas Fooyya\'ii\n\n🎮 Tapha Taphatame: {current}/10\n🎯 Tapha Barbaachisan: {needed}\n\nBonas 20 ETB argachuuf tapha walitti fufan {needed} dabalataa taphadi!',
        'error_occurred': 'Dogoggorri ta\'e. Maaloo booda itti yaali.'
    },
    'so': {
        'welcome': 'Ku soo dhawoow Liyu Bingo!',
        'select_language': 'Fadlan dooro luqaddaada:',
        'play': '🎮 Ciyaar',
        'register': '📝 Isdiiwaangeli',
        'check_balance': '💰 Hubi dheelka',
        'deposit': '💳 Lacag geli',
        'contact_support': '📞 Hel taageero',
        'instructions': '📚 Tilmaamaha',
        'leaderboard': '🏆 Hogaamiyayaasha',
        'english': '🇺🇸 English',
        'amharic': '🇪🇹 Amharic',
        'oromo': '🇪🇹 Oromo',
        'somali': '🇸🇴 Soomaali',
        'tigrinya': '🇪🇹 Tigrinya',
        'user_not_found': 'Isticmaalaha lama heli. Fadlan marka hore isdiiwaangeli.',
        'bonus_earned': '🎉 Hambalyo! Waxaad heshay bonus!\n\n💰 Qadarka Bonus: {amount:.2f} ETB\n🎮 Ciyaaraha Isku Xiga: {games}\n\nBonuskaaga ayaa lagu daray walletkaaga. Si aad u hesho bonusyo dheeraad ah ciyaar sii wad!',
        'bonus_progress': '📊 Horumarka Bonuska Ciyaaraha Isku Xiga\n\n🎮 Ciyaaraha La Ciyaaray: {current}/10\n🎯 Ciyaaraha Loo Baahan Yahay: {needed}\n\nSi aad u hesho bonus 20 ETB ciyaar isku xiga {needed} dheeraad ah ciyaar!',
        'error_occurred': 'Qalad ayaa dhacay. Fadlan dib u isku day.'
    },
    'ti': {
        'welcome': 'ናይ ሊዩ ቢንጎ እንቋዕ ብደሓን መጻእኩም!',
        'select_language': 'ቋንቋኹም ምረጹ:',
        'play': '🎮 ተጻወቱ',
        'register': '📝 ተመዝግቡ',
        'check_balance': '💰 ሚዛን ምርመራ',
        'deposit': '💳 ገንዘብ ኣብልዑ',
        'contact_support': '📞 ሓገዝ ረኸቡ',
        'instructions': '📚 መምርሒታት',
        'leaderboard': '🏆 ኣሸናፊታት',
        'english': '🇺🇸 English',
        'amharic': '🇪🇹 Amharic',
        'oromo': '🇪🇹 Oromo',
        'somali': '🇸🇴 Somali',
        'tigrinya': '🇪🇹 ትግርኛ',
        'user_not_found': 'ተጠቃሚ ኣይተረኽበን። በጃኹም ብመጀመርታ ተመዝግቡ።',
        'bonus_earned': '🎉 እንቋዕ ደስ ኢልኩም! ቦነስ ረኺብኩም!\n\n💰 ዋጋ ቦነስ: {amount:.2f} ETB\n🎮 ተኸታታይ ጸወታታት: {games}\n\nቦነስኩም ናብ ዋለትኩም ተወሲኹ። ተወሳኺ ቦነስ ንምርካብ ጸወታ ቀጽሉ!',
        'bonus_progress': '📊 ተኸታታይ ጸወታታት ቦነስ ምዕባለ\n\n🎮 ዝተጸወቱ ጸወታታት: {current}/10\n🎯 ዘድልዩ ጸወታታት: {needed}\n\nቦነስ 20 ETB ንምርካብ {needed} ተወሳኺ ተኸታታይ ጸወታ(ታት) ጸወቱ!',
        'error_occurred': 'ጌጋ ተፈጢሩ። በጃኹም ድሕሪ እንደገና ፈትኑ።'
    }
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def get_user_language(user_id):
    """Get user's language preference from user_data, default to English"""
    return user_data.get(user_id, {}).get('language', 'en')

def get_text(user_id, key):
    """Get localized text for user"""
    lang = get_user_language(user_id)
    return LANGUAGE_TEXTS[lang].get(key, LANGUAGE_TEXTS['en'][key])

def language_selection_keyboard():
    """Create language selection keyboard"""
    keyboard = [
        [InlineKeyboardButton("🇺🇸 English", callback_data='lang_en')],
        [InlineKeyboardButton("🇪🇹 አማርኛ", callback_data='lang_am')],
        [InlineKeyboardButton("🇪🇹 Afaan Oromoo", callback_data='lang_om')],
        [InlineKeyboardButton("🇸🇴 Soomaali", callback_data='lang_so')],
        [InlineKeyboardButton("🇪🇹 ትግርኛ", callback_data='lang_ti')]
    ]
    return InlineKeyboardMarkup(keyboard)

def main_menu_keyboard(user_id):
    """Create main menu keyboard based on user's language"""
    lang = get_user_language(user_id)
    texts = LANGUAGE_TEXTS[lang]
    
    keyboard = [
        [InlineKeyboardButton(texts['play'], callback_data='play'),
         InlineKeyboardButton(texts['register'], callback_data='register')],
        [InlineKeyboardButton(texts['check_balance'], callback_data='check_balance'),
         InlineKeyboardButton(texts['deposit'], callback_data='deposit')],
        [InlineKeyboardButton(texts['leaderboard'], callback_data='leaderboard'),
         InlineKeyboardButton(texts['instructions'], callback_data='instructions')],
        [InlineKeyboardButton(texts['contact_support'], callback_data='contact_support')],
    ]
    return InlineKeyboardMarkup(keyboard)

# ============ Local mode (no external API calls) ============
LOCAL_MODE = True  # set True to use ORM instead of HTTP API

def local_get_user_by_telegram(telegram_id: int):
    try:
        return User.objects.get(telegram_id=str(telegram_id))
    except User.DoesNotExist:
        return None

def local_get_wallet_by_telegram(telegram_id: int):
    user = local_get_user_by_telegram(telegram_id)
    if not user:
        return {"balance": 0.0, "total_referral_earnings": 0.0}
    wallet, _ = Wallet.objects.get_or_create(user=user)
    # total_referral_earnings kept on user model
    return {
        "balance": float(wallet.balance or 0.0),
        "total_referral_earnings": float(user.total_referral_earnings or 0.0),
        "referral_bonus": float(user.total_referral_earnings or 0.0),
    }

def local_get_payment_settings():
    ps = PaymentSettings.get_solo()
    return {
        "min_deposit_amount": float(ps.min_deposit_amount or 0.0),
        "min_withdrawal_amount": float(ps.min_withdrawal_amount or 0.0),
        "max_withdrawal_amount": float(ps.max_withdrawal_amount or 0.0),
        "withdrawal_fee_percent": float(ps.withdrawal_fee_percent or 0.0),
    }

def local_create_withdrawal_request(telegram_id: int, amount: float, withdraw_account: str = ""):
    user = local_get_user_by_telegram(telegram_id)
    if not user:
        return {"success": False, "message": "User not found"}
    try:
        wr = WithdrawalRequest.objects.create(user=user, amount=amount, status="pending")
        return {"success": True, "id": wr.id}
    except Exception as e:
        return {"success": False, "message": str(e)}

def local_get_user_games_week_count(telegram_id: int):
    user = local_get_user_by_telegram(telegram_id)
    if not user:
        return 0
    today = timezone.now().date()
    start_of_week = today - timezone.timedelta(days=today.weekday())
    end_of_week = start_of_week + timezone.timedelta(days=6)
    return Transaction.objects.filter(
        user=user, type="BET", created_at__date__gte=start_of_week, created_at__date__lte=end_of_week
    ).count()

def generate_nonce(length=64):
    characters = string.ascii_letters + string.digits + string.punctuation
    nonce = ''.join(random.choice(characters) for _ in range(length))
    return nonce


def generate_tx_ref(length=20):
    """Generate a transaction reference that contains only letters, numbers, hyphens, underscores, and dots."""
    characters = string.ascii_letters + string.digits + '-_.'
    tx_ref = ''.join(random.choice(characters) for _ in range(length))
    return tx_ref


# Define conversation states
DEPOSIT_AMOUNT = range(1)
SCREENSHOT = range(2)
GET_DEPOSIT_AMOUNT,WITHDRAW_AMOUNT_CONFIRM,WITHDRAW_AMOUNT_CANCEL,CHOOSE_PAYMENT_METHOD,GET_WITHDRAW_ACCOUNT,GET_TRANSCATION_DETAILS,PHONE,REGISTER,SOME_STATE,WAIT_FOR_PAYMENT = range(2,12)

CONVERSATION_TIMEOUT = 300  # 5 minutes



async def conversation_timeout(context):
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Conversation timed out due to inactivity. Please start again."
    )



    
    


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    
    # Extract referral info from deep link if present
    referrer_id = None
    print(f"DEBUG: start command - context.args = {context.args}")
    if context.args and len(context.args) > 0:
        print(f"DEBUG: Processing args[0] = {context.args[0]}")
        try:
            # Check if it's a ref_ format
            if context.args[0].startswith("ref_"):
                referrer_id = int(context.args[0].split("_")[1])
                print(f"DEBUG: Extracted referrer_id from ref_ format: {referrer_id}")
            else:
                referrer_id = int(context.args[0])
                print(f"DEBUG: Direct referrer_id: {referrer_id}")
            
            # Check if referrer is eligible (has made deposits)
            from register import is_referrer_eligible
            is_eligible = await is_referrer_eligible(referrer_id)
            if not is_eligible:
                await update.message.reply_text("❌ This referral link is not eligible!")
                await update.message.reply_text("The referrer has not made any deposits yet.")
                await update.message.reply_text("Please register without a referral link or use a different referral link.")
                return
            
            # Store referrer ID in user data for later use
            context.user_data['referrer_id'] = referrer_id
            print(f"DEBUG: Stored referrer_id in context: {context.user_data['referrer_id']}")
        except ValueError:
            logger.warning(f"Invalid referrer ID format: {context.args[0]}")
        except Exception as e:
            logger.error(f"Error processing referrer_id: {e}")
    else:
        print("DEBUG: No args provided to start command")
    
    # Check if user has already selected a language
    if user_id in user_data and 'language' in user_data[user_id]:
        # User has language preference, show main menu
        await show_main_menu(update, context)
    else:
        # Show language selection
        await show_language_selection(update, context)
    
    return SOME_STATE

async def show_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show language selection menu"""
    reply_markup = language_selection_keyboard()
    await update.message.reply_text(
        'Welcome to Liyu Bingo!\n\n'
        'Please select your language:\n'
        'እባክዎ ቋንቋዎን ይምረጡ:\n'
        'Maaloo afaan kee filadhu:\n'
        'Fadlan dooro luqaddaada:\n'
        'ቋንቋኹም ምረጹ:',
        reply_markup=reply_markup
    )

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu based on user's language"""
    user_id = update.effective_user.id
    reply_markup = main_menu_keyboard(user_id)
    welcome_text = get_text(user_id, 'welcome')
    
    await update.message.reply_text(f'{welcome_text}! Select an option:', reply_markup=reply_markup)
    context.job_queue.run_once(conversation_timeout, CONVERSATION_TIMEOUT, chat_id=update.effective_chat.id)
    return SOME_STATE


# Function to create the play options keyboardF
def play_options_keyboard(update: Update) -> InlineKeyboardMarkup:
    logger.info("open the play game link")
    return InlineKeyboardMarkup([[InlineKeyboardButton("🎮 Play Game", url="https://t.me/liyuchewatabotbot/liyuchawata")]])




async def get_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
   
    await update.message.reply_text("Please enter the amount you want to withdraw:")
    return WITHDRAW_AMOUNT_CONFIRM

def deposit_opitions_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("💳 Deposit with Telebirr", callback_data='manual_telebirr')],
        [InlineKeyboardButton("💳 Deposit with CBE", callback_data='manual_cbe')],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def withdraw_opitions_keyboard(context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
    logger.info("withdraw_opitions_keyboard")
    banks = {}
    logger.info(f"banks = {banks}")
    # Only show Telebirr and CBE options
    keyboard = []
    banks_to_bank_id = {
         'Telebirr':855,
        'CBE': 946
    }
    
    keyboard.append([InlineKeyboardButton("Telebirr", callback_data='withraw_with_telebirr')])
    keyboard.append([InlineKeyboardButton("CBE", callback_data='withraw_with_cbe')])
    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data='menu')])
    context.user_data['banks_to_bank_id'] = banks_to_bank_id

    return InlineKeyboardMarkup(keyboard)



   

async def withdraw_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = withdraw_opitions_keyboard(context) 
    await update.message.reply_text("Choose a withdraw method", reply_markup=reply_markup)


async def get_withdraw_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = update.message.text
    telegram_id = update.effective_user.id
    
    logger.info(f"telegram_id {telegram_id}")
    logger.info(f"amount {amount}")
 
    try:
        # Get user and wallet using Django ORM
        user = await get_user_by_telegram_id(telegram_id)
        if not user:
            await update.message.reply_text("User not found. Please register first.")
            return ConversationHandler.END
            
        # Get payment settings using Django ORM
        settings_json = await get_payment_settings()
        min_withdrawal = float(settings_json.get('min_withdrawal_amount', 50))
        max_withdrawal = float(settings_json.get('max_withdrawal_amount', 100))
        
        # Get wallet with referral earnings using Django ORM
        wallet_data = await get_user_wallet_with_referrals(user)
        balance = wallet_data.get('total_balance', 0)

        # Check daily withdrawal limit using Django ORM
        has_reached_daily_limit = await daily_withdraw_limit(telegram_id)
        logger.info(f"daily_withdraw_limit reached: {has_reached_daily_limit}")
        if has_reached_daily_limit:
            await update.message.reply_text(f"You have reached the daily withdraw limit. Please try again tomorrow.")
            return WITHDRAW_AMOUNT_CONFIRM
            
        # Check if user has deposited using Django ORM
        is_deposited = await is_deposited_player(telegram_id)
        if not is_deposited:
            await update.message.reply_text(f"You need to deposit first. 50 ETB minimum deposit is required to withdraw.")
            return WITHDRAW_AMOUNT_CONFIRM

        # Check games played and won using Django ORM
        number_game_played = await numnber_of_game_played(telegram_id)
        number_game_won = await number_of_game_won(telegram_id)

        if int(number_game_played) < 5:
            await update.message.reply_text(f"ከ 5 ጨወታ በላይ መጫዎት አለብዎት")
            return WITHDRAW_AMOUNT_CONFIRM

        if int(number_game_won) < 2:
            await update.message.reply_text(f"2 ጨወታ ማሽነፍ አለብዎት")
            return WITHDRAW_AMOUNT_CONFIRM

        # Enforce PaymentSettings min/max
        if float(amount) > max_withdrawal and max_withdrawal > 0:
            await update.message.reply_text(f"Withdrawal amount must be less than or equal to {max_withdrawal:.0f} ETB")
            return WITHDRAW_AMOUNT_CONFIRM

        if int(balance) < 20:
            await update.message.reply_text(f"You must leave at least 20 ETB in your wallet. Please enter a smaller amount.")
            return WITHDRAW_AMOUNT_CONFIRM

        if float(amount) < min_withdrawal:
            await update.message.reply_text(f"Withdrawal amount must be at least {min_withdrawal:.0f} ETB")
            return WITHDRAW_AMOUNT_CONFIRM

        # Check if withdrawal amount exceeds balance
        if int(amount) > int(balance):
            await update.message.reply_text(f"Insufficient funds. Your current balance is {balance} ETB")
            return WITHDRAW_AMOUNT_CONFIRM
        else:
            # Optional: Trigger async validation task for additional checks
            validation_task = await trigger_withdrawal_validation(telegram_id, float(amount))
            if validation_task:
                logger.info(f"Withdrawal validation task triggered: {validation_task.id}")
            
            # Store amount in context for later use
            context.user_data['withdraw_amount'] = amount
            logger.info(f"context.user_data['withdraw_amount'] {context.user_data['withdraw_amount']}") 
            banks_to_bank_id = context.user_data['banks_to_bank_id']
            logger.info(f"banks_to_bank_id {banks_to_bank_id}")
            bank_name = banks_to_bank_id.get(context.user_data['bank_id'])
            logger.info(f"bank_name {bank_name}")
            await update.message.reply_text(
                f"Please enter your {bank_name} number  where you want to receive the withdrawal:"
            )
            return GET_WITHDRAW_ACCOUNT
        
    except Exception as e:
        logger.error(f"Error checking wallet balance: {e}")
        await update.message.reply_text("Error checking your balance. Please try again later.")
        return ConversationHandler.END
  
        
  



async def get_withdraw_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    account_number = update.message.text
    try:
        withdraw_amount = float(context.user_data['withdraw_amount'])
        user_telegram_id = update.effective_user.id

        # Get user using Django ORM
        user = await get_user_by_telegram_id(user_telegram_id)
        if not user:
            await update.message.reply_text("User not found. Please register first.")
            return ConversationHandler.END

        # Get bank name from context
        banks_to_bank_id = context.user_data.get('banks_to_bank_id', {})
        bank_id = context.user_data.get('bank_id', '')
        bank_name = banks_to_bank_id.get(bank_id, 'Bank')

        # Create withdrawal request using Django ORM
        withdrawal_request = await create_withdrawal_request(
            user=user,
            amount=withdraw_amount,
            phone_number=account_number,
            account_name=account_number,
            bank_name=bank_name,
            withdrawal_method='bank_transfer'
        )

        if withdrawal_request:
            # Send immediate confirmation
            await update.message.reply_text(
                "✅ Your withdrawal request has been submitted. We will review and process it shortly.\n\n"
                f"Amount: {withdraw_amount} ETB\n"
                f"Account: {account_number}\n"
                f"Bank: {bank_name}\n"
                f"Reference: WITHDRAW_{withdrawal_request.id}\n\n"
                "You will receive a notification when the processing is complete."
            )
            
            logger.info(f"Withdrawal request created: ID={withdrawal_request.id}, User={user.username}, Amount={withdraw_amount}")
                
        else:
            await update.message.reply_text(
                "❌ Failed to submit withdrawal request. Please try again later."
            )

        return ConversationHandler.END
    except Exception as e:
        print(f"Error sending message to user: {e}")
        await update.message.reply_text("❌ An error occurred. Please try again later.")
        return ConversationHandler.END



async def get_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Get user and wallet using Django ORM
    user = await get_user_by_telegram_id(user_id)
    if not user:
        return 0
        
    wallet = await get_user_wallet(user)
    balance = wallet.balance if wallet else 0
    return balance


async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = play_options_keyboard(update) 
    balance = await get_balance(update, context)
    try:
        logger.info(f"User {update.effective_user.username} balance: {balance}")
    except Exception as e:
        print(f"Error getting wallet balance: {e}")
  
    await update.message.reply_text("Choose a play option:", reply_markup=reply_markup)



# Function to create the play options keyboard
def instructions_options_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("📝 Registraion", callback_data='register_instructions'),
            InlineKeyboardButton("🎮 Game play ", callback_data='play_instruction')
         ],
        [
            InlineKeyboardButton("💰 Deposit", callback_data='deposit_instruction'),
            InlineKeyboardButton("💰 Withdraw", callback_data='withdraw_instruction')
         ],
         [InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]
    ]
    

    return InlineKeyboardMarkup(keyboard)









async def instruction_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Read and display instructions.html content directly
    try:
        with open('instructions.html', 'r', encoding='utf-8') as file:
            instruction_content = file.read()
        
        # Create keyboard with back button
        keyboard = [
            [InlineKeyboardButton("🔙 Back to Menu", callback_data='menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text=instruction_content,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    except FileNotFoundError:
        await update.message.reply_text(
            text="Instructions file not found. Please contact support."
        )
    except Exception as e:
        logger.error(f"Error reading instructions: {e}")
        await update.message.reply_text(
            text="An error occurred while loading instructions. Please try again later."
        )




async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    BACK_URL = get_bot_seetings().get("bot_url")
    username = query.from_user.username 
    await query.answer()
  

    try:
        # Get game types for validation
        game_types_response = await get_game_type()
        game_types = game_types_response.get('game_types', []) if game_types_response else []
        if query.data in ['10', '20', '50', '100'] or query.data in [str(game_type['bet_amount']) for game_type in game_types]:
            user_id = query.from_user.id
            
            # Check if user exists and is registered using Django ORM
            user = await get_user_by_telegram_id(user_id)
            if not user or not user.phone:
                await query.edit_message_text(
                    text="You need to register first before playing. Use the /register command.",
                    reply_markup=instructions_options_keyboard()
                )
                return
            bet_amount = int(query.data)
            
            # Get user and wallet using Django ORM
            wallet = await get_user_wallet(user)
            balance = wallet.balance if wallet else 0
            # Add referral earnings if available
            balance += getattr(user, 'total_referral_earnings', 0) if user else 0
           
          
            if balance < bet_amount:
                await query.edit_message_text(
                    text=f"Insufficient balance. Your current balance is {balance} ETB. Please deposit more to play.",
                    reply_markup=deposit_opitions_keyboard()
                )
                return

            player_id = query.from_user.id
            web_app_url = f"https://t.me/liyuchewatabotbot/liyuchawata"
            
            await query.edit_message_text(
                text=f"Starting game with {bet_amount} ETB bet...",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Play Game", web_app=WebAppInfo(url=web_app_url))
                ]])
            )
            
           
            return ConversationHandler.END
    
        elif query.data.startswith('withraw_with_'):
            bank_id = query.data.split('_')[2]
            context.user_data['bank_id'] = bank_id
            await query.edit_message_text(
                text="Please enter your withdraw amount ")
            return WITHDRAW_AMOUNT_CONFIRM

        elif query.data == 'withdraw_confirm':
            return WITHDRAW_AMOUNT_CONFIRM
            
        # Handle language selection
        if query.data == 'lang_en':
            user_id = query.from_user.id
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]['language'] = 'en'
            await query.edit_message_text(
                text="Language set to English! 🇺🇸\n\nWelcome to Liyu Bingo! Select an option:",
                reply_markup=main_menu_keyboard(user_id)
            )
            return SOME_STATE
            
        elif query.data == 'lang_am':
            user_id = query.from_user.id
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]['language'] = 'am'
            await query.edit_message_text(
                text="ቋንቋ ወደ አማርኛ ተቀይሯል! 🇪🇹\n\nወደ ሊዩ ቢንጎ እንኳን ደህና መጡ! አማራጭ ይምረጡ:",
                reply_markup=main_menu_keyboard(user_id)
            )
            return SOME_STATE
            
        elif query.data == 'lang_om':
            user_id = query.from_user.id
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]['language'] = 'om'
            await query.edit_message_text(
                text="Afaan Afaan Oromootti jijjirame! 🇪🇹\n\nLiyu Bingo irratti baga nagaan dhufte! Filannoo filadhu:",
                reply_markup=main_menu_keyboard(user_id)
            )
            return SOME_STATE
            
        elif query.data == 'lang_so':
            user_id = query.from_user.id
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]['language'] = 'so'
            await query.edit_message_text(
                text="Luqadda Soomaaliga loo bedelay! 🇸🇴\n\nKu soo dhawoow Liyu Bingo! Dooro xulashada:",
                reply_markup=main_menu_keyboard(user_id)
            )
            return SOME_STATE
            
        elif query.data == 'lang_ti':
            user_id = query.from_user.id
            if user_id not in user_data:
                user_data[user_id] = {}
            user_data[user_id]['language'] = 'ti'
            await query.edit_message_text(
                text="ቋንቋ ናብ ትግርኛ ተለዊጡ! 🇪🇹\n\nናይ ሊዩ ቢንጎ እንቋዕ ብደሓን መጻእኩም! ምርጫ ምረጹ:",
                reply_markup=main_menu_keyboard(user_id)
            )
            return SOME_STATE
            
        if query.data == 'play' :
            user_id = query.from_user.id
            play_text = get_text(user_id, 'play')
            await query.edit_message_text(
                text=f"{play_text} - Choose a play option:",
                reply_markup=play_options_keyboard(update)
            )

        elif query.data == 'contact_support':
            user_id = query.from_user.id
            support_text = get_text(user_id, 'contact_support')
            await query.edit_message_text(
                text=f"{support_text} - Contact us using support button",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📞 Support",  url='https://t.me/LiyuChawata')]])
            )
            return


          
        
        elif query.data == 'instructions':
            user_id = query.from_user.id
            instructions_text = get_text(user_id, 'instructions')
            await query.edit_message_text(
                text=f"{instructions_text} - Choose an instruction option:",
                reply_markup=instructions_options_keyboard()
            )
        
        elif query.data == 'register_instructions':
            # Read and display registration instructions from instructions.html
            try:
                with open('instructions.html', 'r', encoding='utf-8') as file:
                    instruction_content = file.read()
                await query.edit_message_text(
                    text=instruction_content,
                    parse_mode=ParseMode.HTML
                )
            except FileNotFoundError:
                await query.edit_message_text(
                    text="Instructions file not found. Please contact support.",
                    reply_markup=instructions_options_keyboard()
                )
        
        elif query.data == 'play_instruction':
            # Read and display game play instructions from instructions.html
            try:
                with open('instructions.html', 'r', encoding='utf-8') as file:
                    instruction_content = file.read()
                await query.edit_message_text(
                    text=instruction_content,
                    parse_mode=ParseMode.HTML
                )
            except FileNotFoundError:
                await query.edit_message_text(
                    text="Instructions file not found. Please contact support.",
                    reply_markup=instructions_options_keyboard()
                )
        
        elif query.data == 'deposit_instruction':
            # Read and display deposit instructions from instructions.html
            try:
                with open('instructions.html', 'r', encoding='utf-8') as file:
                    instruction_content = file.read()
                await query.edit_message_text(
                    text=instruction_content,
                    parse_mode=ParseMode.HTML
                )
            except FileNotFoundError:
                await query.edit_message_text(
                    text="Instructions file not found. Please contact support.",
                    reply_markup=instructions_options_keyboard()
                )
        
        elif query.data == 'withdraw_instruction':
            # Read and display withdrawal instructions from instructions.html
            try:
                with open('instructions.html', 'r', encoding='utf-8') as file:
                    instruction_content = file.read()
                await query.edit_message_text(
                    text=instruction_content,
                    parse_mode=ParseMode.HTML
                )
            except FileNotFoundError:
                await query.edit_message_text(
                    text="Instructions file not found. Please contact support.",
                    reply_markup=instructions_options_keyboard()
                )
        elif query.data == 'get_deposit_amount':
            return DEPOSIT_AMOUNT
        elif query.data == 'check_balance':
            telegram_id = query.from_user.id
            username = query.from_user.username
            first_name = query.from_user.first_name
            last_name = query.from_user.last_name
            
            try:
                logger.info(f"Checking balance for user {telegram_id}")
                
                # Get user using Django ORM
                user = await get_user_by_telegram_id(telegram_id)
                if not user:
                    await query.edit_message_text("❌ User not found. Please register first.")
                    return
                
                # Get wallet with referral earnings using Django ORM
                wallet_data = await get_user_wallet_with_referrals(user)
                balance = wallet_data.get('total_balance', 0)
                
                # Get user game statistics using Django ORM
                game_stats = await get_user_game_statistics(user)
                games_played_this_week = game_stats.get('games_played_this_week', 0)
                
                # Create payment summary with user details and weekly progress
                payment_summary = (
                    "🏦 Liyu Bingo BINGO STATEMENT\n" +
                    f"💰  {balance} Birr\n" +
                    f"👥  {first_name} \n" +
                    f"📄 Transaction ID: {telegram_id}\n\n" +
                    f"🔙 Back to Menu\n" 
                ) 
                await query.edit_message_text(text=payment_summary)
                return
                
            except Exception as e:
                logger.error(f"Error checking balance: {e}")
                await query.edit_message_text("❌ Error fetching your balance. Please try again later.")
                return
        elif query.data in ['10','20']:
            player_id = query.from_user.id
            user_id = query.from_user.id
            username = query.from_user.username or query.from_user.first_name
            bet_amount = int(query.data)
            
            # Check if user is registered using Django ORM
            user = await get_user_by_telegram_id(user_id)
            if not user or not user.phone:
                await query.edit_message_text(
                    text="You need to register first before playing. Use the /register command.",
                    reply_markup=instructions_options_keyboard()
                )
                return
            
            # Check wallet balance using Django ORM
            wallet_data = await get_user_wallet_with_referrals(user)
            balance = wallet_data.get('total_balance', 0)
            
            # Check if balance is sufficient
            if balance < bet_amount:
                await query.edit_message_text(
                    text=f"Insufficient balance. Your current balance is {balance} ETB. Please deposit more to play.",
                    reply_markup=deposit_opitions_keyboard()
                )
                return
            
            web_app_url = (
                f"https://liyuchawata.akerbingo.com/?playerId={player_id}&name={username}&betAmount={bet_amount}&wallet_amount={balance}"
            )

            keyboard = [
                [InlineKeyboardButton("Open Liyu Bingo!", web_app=WebAppInfo(url=web_app_url))]
                # [InlineKeyboardButton("Open Wow Bingo!", url=web_app_url)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Start playing Liyu bingo", reply_markup=reply_markup)

        elif query.data == 'leaderboard':
            # Call the leaderboard command from helpers
            await leaderboard_command(query, context)

        elif query.data == 'deposit':
            await query.edit_message_text(
                text="💰 እንዲሞላልዎት የሚፈልጉትን የገንዘብ መጠን ያስገቡ:"
            )
            context.user_data['deposit_amount'] = query.data
            return DEPOSIT_AMOUNT
           
        elif query.data == 'get_deposit_amount_of_telebirr':

            await query.edit_message_text(
                text="Please enter your deposit amount in this :"
            )
            
            return DEPOSIT_AMOUNT

        elif query.data == 'get_deposit_amount_of_cbe_bank':
            await query.edit_message_text(
                text="Please enter your deposit amount in this:"
            )
            return DEPOSIT_AMOUNT

        # Removed legacy Chapa branch
    
 
        
        elif query.data == 'cancel':
            await query.edit_message_text(text="Withdrawal request cancelled.")
            return ConversationHandler.END


        
        elif query.data == "register":
            user_id = query.from_user.id
            register_text = get_text(user_id, 'register')
            
            # Debug: Check if referrer_id is in context
            print(f"DEBUG: register callback - context.user_data: {context.user_data}")
            referrer_id = context.user_data.get('referrer_id')
            print(f"DEBUG: register callback - referrer_id: {referrer_id}")
            
            # Use a ReplyKeyboardMarkup with request_contact to actually receive phone number
            contact_keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton(text="📞 Share Phone Number", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            await query.message.reply_text(
                text=f"{register_text} - Tap the button below to share your phone number.",
                reply_markup=contact_keyboard
            )
            return REGISTER

        elif query.data == 'manual':
            keyboard = [
                [InlineKeyboardButton("Telebirr", callback_data='manual_telebirr')],
                [InlineKeyboardButton("CBE", callback_data='manual_cbe')],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data='menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text(text="Please select a payment method:", reply_markup=reply_markup)

        elif query.data == "manual_telebirr":
            filepath = "telebirr_message.html"
            with open(filepath, 'r') as file:
                message = file.read()
            context.user_data['payment_method'] = 'manual_telebirr'
            # Debug: Log deposit_amount to ensure it's preserved
            logger.info(f"Manual Telebirr selected. Deposit amount in context: {context.user_data.get('deposit_amount', 'NOT FOUND')}")
            await query.edit_message_text(text=message, parse_mode=ParseMode.HTML)
            return WAIT_FOR_PAYMENT

        elif query.data == "manual_cbe":
            filepath = "cbe_message.html"
            with open(filepath, 'r') as file:
                message = file.read()
            await query.edit_message_text(text=message, parse_mode=ParseMode.HTML)
            context.user_data['payment_method'] = 'manual_cbe'
            # Debug: Log deposit_amount to ensure it's preserved
            logger.info(f"Manual CBE selected. Deposit amount in context: {context.user_data.get('deposit_amount', 'NOT FOUND')}")
            return WAIT_FOR_PAYMENT
    
        elif query.data == 'share_phone':
            # Fallback in case the inline button is used elsewhere
            contact_keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton(text="📞 Share Phone Number", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            await query.edit_message_text(text="📱 Please share your phone number to register:")
            await query.message.reply_text(
                text="Tap the button below to share your phone number.",
                reply_markup=contact_keyboard
            )
            return REGISTER
           
    
          
        elif query.data == 'menu':
            keyboard = [
                [InlineKeyboardButton("Play Game", callback_data='play'),
                 InlineKeyboardButton("Check Balance", callback_data='check_balance'),
                 InlineKeyboardButton("Withdraw", callback_data='withdraw')],
                [InlineKeyboardButton("Deposit", callback_data='deposit'),
                 InlineKeyboardButton("Register", callback_data='register_menu')]

              
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Welcome to Liyu Bingo! Please select an option:", reply_markup=reply_markup)
            
            
 
        else:

            keyboard = [
                [InlineKeyboardButton("Play Game", callback_data='play'),
                 InlineKeyboardButton("Check Balance", callback_data='check_balance')],
                [InlineKeyboardButton("Deposit", callback_data='deposit'),
                 InlineKeyboardButton("Register", callback_data='register_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Welcome to Liyu Bingo! Please select an option:", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error handling query: {query.data} - {e}")
        await query.edit_message_text(text="An error occurred. Please try again.")


async def show_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to show user's unique ID"""
    try:
        print("DEBUG: show_id_command called")
        user_id = update.effective_user.id
        username = update.effective_user.username or "User"
        
        print(f"DEBUG: user_id = {user_id}, username = {username}")
        
        # Create the unique ID in the format Liyu_telegramid
        unique_id = f"Liyu_{user_id}"
        
        message = (
            f"🆔 Your Unique ID\n\n"
            f"ID: <code>{unique_id}</code>\n"
            f"Username: {username}\n\n"
            f"📋 You can copy the ID above to share with others.\n"
        )
        
        print(f"DEBUG: Sending message: {message}")
        await update.message.reply_text(message, parse_mode=ParseMode.HTML)
        print("DEBUG: Message sent successfully")
        
    except Exception as e:
        print(f"DEBUG: Error in show_id_command: {e}")
        logger.error(f"Error in show_id_command: {e}")
        await update.message.reply_text("❌ Error showing your ID. Please try again.")
    
    return ConversationHandler.END


async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command to contact support"""
    await update.message.reply_text(
        "📞 **Contact Support**\n\n"
        "Need help? Our support team is here to assist you!\n\n"
        "🔗 Contact us: https://t.me/adaa_alepo\n"
    )

async def deposit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    amount = update.message.text

    if float(amount) <=49:
        await update.message.reply_text("Minimum deposit amount is 50 ETB. Please enter a higher amount.")
        return DEPOSIT_AMOUNT

    back_url = get_bot_seetings().get("bot_url")
   
    full_url = f"{back_url}/api/v1/users/{update.effective_user.id}"
    logger.info(f"full_url = {full_url}")

    response = requests.get(full_url)
    try:
        response_data = response.json()
        print("wow pay bot url ", response_data)
        phone = response_data.get("phone")
    except requests.exceptions.JSONDecodeError:
        print("Invalid JSON response from API")
        phone = None
    print("phone = ",phone)
    context.user_data['deposit_amount'] = amount    

    message = """
    <b>💳 Payment Receipt</b>
    <b>👤 Name:</b> {}  
    <b>📞 Phone:</b> {}  
    <b>💰 Amount:</b> {} ETB  
    <b>📅 Date:</b> {}
    """.format(update.effective_user.username,phone,amount,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    inline_keyboard = [
        # [
        #         # InlineKeyboardButton("Chapa", callback_data='chapa'),
        #         InlineKeyboardButton("Telebirr", callback_data='chapa_telebirr'),
        #         InlineKeyboardButton("CBE", callback_data='chapa_cbe')

        #     # InlineKeyboardButton("AddisPay", callback_data='addispay')
        # ],
        [
            InlineKeyboardButton("Manual", callback_data='manual')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    await update.message.reply_text(message,parse_mode=ParseMode.HTML,reply_markup=reply_markup)
    
   
  



async def get_transcation_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  
    message = update.message.text
    try:
        parsed_data = json.loads(message)
        amount = parsed_data.get('amount')
        user_id = update.effective_user.id
        username = update.effective_user.username
        transaction_number = parsed_data.get('transaction_details')['id']
    except json.JSONDecodeError:
        await update.message.reply_text("Invalid transaction data format.")
        return ConversationHandler.END

    print("transaction_number = ",transaction_number)
    
    BACK_URL = get_bot_seetings().get("bot_url")
    response = requests.get(f'{BACK_URL}/transactions/transactionId/{transaction_number}')
    res = response.json()
    if res.get('status') == 'error':
        await update.message.reply_text("Transaction Does not exist.")
        return ConversationHandler.END
    res_amount = res.get('amount').get('value')
    try:
        _cb = requests.get(f'{BACK_URL}/users/{user_id}/')
        current_balance = (_cb.json().get('user',{}).get('balance',0)) if _cb.headers.get('content-type','').startswith('application/json') else 0
        response = requests.put(f'{BACK_URL}/users/balance/{user_id}/', json={"balance": current_balance + res_amount})
        withdraw_response = requests.delete(f'{BACK_URL}/transactions/{transaction_number}')
        
        message = response.json()
        if message.get('status') == 'success':
           
            await update.message.reply_text(message.get('message'))
            return ConversationHandler.END  
        else:
            await update.message.reply_text(message.get('message'))
            return ConversationHandler.END
    except Exception as e:
        print("error = ",e)
        await update.message.reply_text("An error occurred. Please try again.")
        return ConversationHandler.END


all_public_commands_descriptions = [
   
    BotCommand(
        "register", 
        "Register"
        ),

    BotCommand(
        "play", 
        "Play"
        ),

 

    BotCommand(
        "check_balance", 
        "Balance"
        ),

    BotCommand(
        "deposit", 
        "Deposit"
        ),

    BotCommand(
        "withdraw", 
        "Withdraw"
        ),

    BotCommand(
        "instructions", 
        "Instructions"
        ),


    BotCommand(
            "start", 
            "Start"
        ),

      BotCommand(
        "support", 
        "Contact us"
        ),


    BotCommand(
        "invite", 
        "Invite"
        ),

    BotCommand(
        "redeem", 
        "Redeem Bonus"
        ),

 
    ]


async def post_init(app):
    await app.bot.set_my_commands(all_public_commands_descriptions)


      
  

async def handle_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    BACK_URL = get_bot_seetings().get("bot_url")
    user_id = update.effective_user.id
    referrer_id = context.user_data.get('referrer_id')
    logger.info(f"referrer_id = {referrer_id}")

    # response = requests.get(f'{BACK_URL}/api/v1/users/{user_id}')
    # if response.status_code != 200:
    #     await update.message.reply_text(
    #         "You need to register first before inviting others. Use the /register command."
    #     )
    #     return

    # Get user's wallet balance
    _wr = requests.get(f'{BACK_URL}/api/v1/wallet/player/{user_id}')
    wallet_response = _wr.json() if _wr.headers.get('content-type','').startswith('application/json') else {}
    balance = wallet_response.get('balance', 0)

    telegram_id = update.effective_user.id
    # Get bot username dynamically
    bot_username = (await context.bot.get_me()).username
    # Use ref_ prefix so start command can parse first-generation referrer
    invite_link = f"https://t.me/{bot_username}?start=ref_{telegram_id}"
    message = (
        "Invite your friends to Liyu Bingo and earn rewards!\n\n"
        "Tap the button below to share your invite link with others."
    )
    # Create a share button with the invite link
    share_button = InlineKeyboardButton(
        text="🔗 Share Invite Link",
        switch_inline_query=invite_link
    )
    reply_markup = InlineKeyboardMarkup([[share_button]])
    await update.message.reply_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )



async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("DEBUG: register_command function called")
    print(f"DEBUG: register_command context.user_data: {context.user_data}")
    user_id = update.effective_user.id
    
    # Check if referrer_id is already in context (from start command)
    referrer_id = context.user_data.get('referrer_id')
    print(f"DEBUG: register_command - referrer_id from context: {referrer_id}")
    
    # If not in context, try to get from args
    if not referrer_id and context.args:
        referrer_id = context.args[0] if context.args else None
        context.user_data['referrer_id'] = referrer_id
        print(f"DEBUG: register_command - set referrer_id from args: {referrer_id}")
    
    print(f"DEBUG: register_command final referrer_id = {referrer_id}")
    
    # Check if user is already registered using Django ORM
    user = await get_user_by_telegram_id(user_id)
    if user and user.phone:
        await update.message.reply_text(
            "✅ You are already registered!\n\n"
            "🎮 Click /play to start the game"
            "Use the menu to explore all available options."
        )
        return ConversationHandler.END
    
 
    contact_keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton(text="📞 Share Phone Number", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
    await update.message.reply_text(
                text="Tap the button below to share your phone number.",
                reply_markup=contact_keyboard
            )
    return REGISTER

async def check_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    BACK_URL = get_bot_seetings().get("bot_url")
    telegram_id = update.effective_user.id
    
    try:
        # Get wallet balance
        if LOCAL_MODE:
            wallet_data = await sync_to_async(local_get_wallet_by_telegram, thread_sensitive=True)(telegram_id)
        else:
            wallet_response = requests.get(f'{BACK_URL}/api/v1/wallet/player/{telegram_id}')
            logger.info(f"Wallet API response status: {wallet_response.status_code}")
            wallet_data = wallet_response.json() if wallet_response.headers.get('content-type','').startswith('application/json') else {}
        balance = wallet_data.get('balance', 0)
        logger.info(f"Balance retrieved: {balance}")
        
        # Get user info and game statistics
        if LOCAL_MODE:
            # Not used directly: u
            games_played_this_week = await sync_to_async(local_get_user_games_week_count, thread_sensitive=True)(telegram_id)
        else:
            user_response = requests.get(f'{BACK_URL}/api/v1/users/{telegram_id}')
            logger.info(f"User API response status: {user_response.status_code}")
            user_info = user_response.json() if user_response.headers.get('content-type','').startswith('application/json') else {}
            games_played_this_week = user_info.get('games_played_this_week', 0) or 0
        logger.info(f"Games played this week: {games_played_this_week}")

        # Referral bonus (float) - handle None values
        total_referral_earnings_raw = (wallet_data.get('referral_bonus', 0) if LOCAL_MODE else user_info.get('total_referral_earnings', 0)) or 0
        total_referral_earnings = float(total_referral_earnings_raw) if isinstance(total_referral_earnings_raw, (int, float, str)) else 0.0

        # Compute balances per policy - handle None values
        wallet_balance = float(balance or 0)
        referral_bonus_raw = wallet_data.get('referral_bonus', 0) or 0
        referral_bonus = float(referral_bonus_raw) if isinstance(referral_bonus_raw, (int, float, str)) else 0.0
        threshold_met = referral_bonus >= 500.0
        withdrawable_balance = wallet_balance + (referral_bonus if threshold_met else 0.0)
        total_balance = wallet_balance + referral_bonus 
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request error: {e}")
        await update.message.reply_text("❌ Error fetching your balance. Please try again later.")
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Unexpected error in check_balance: {e}")
        await update.message.reply_text("❌ An unexpected error occurred. Please try again later.")
        return ConversationHandler.END
    
    # Get user info for personalization
    user_name = update.effective_user.first_name or update.effective_user.username or "Player"
    
    # Calculate remaining games needed - ensure games_played_this_week is an integer
    games_played = int(games_played_this_week) if games_played_this_week is not None else 0
    remaining_games = 0

    phone = await get_user_phone(telegram_id)
    if not phone:
        phone = "Not found"
    print("phone = ",phone)
    # Create appealing balance message
    if balance > 0:
        message = (
        f"💰 Hey {user_name}! Your Current Account Balance!\n"
        f"📱 **Phone Number:** {phone}\n"
        f"🎯 **Balance: {balance:.2f} ETB\n"
        f"🎁 **Referral Bonus: {referral_bonus:.2f} ETB\n"
        f"🎯 **Total Balance: {total_balance:.2f} ETB\n"
        f"💵 **Withdrawable Balance: {withdrawable_balance:.2f} ETB\n"

        )
    else:
        message = (
        f"💰 Hey {user_name}! Your Current Account Balance!\n"
        f"📱 **Phone Number:** {phone}\n"
        f"🎯 **Balance: {balance:.2f} ETB\n"
        f"🎁 **Referral Bonus: {referral_bonus:.2f} ETB\n"
        f"🎯 **Total Balance: {total_balance:.2f} ETB\n"
        f"💵 **Withdrawable Balance: {withdrawable_balance:.2f} ETB\n"
       
        )

    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
   
    return ConversationHandler.END

async def deposit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please deposit to play the game.")
    reply_markup = deposit_opitions_keyboard()
    await update.message.reply_text("Choose a deposit option:", reply_markup=reply_markup)
    
    return ConversationHandler.END



async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("DEBUG: start_command function called")
    user_id = update.effective_user.id
    # @testselselambingobot ref_1464395537
    # If the user started the bot with a referral link like @testselselambingobot ref_1464395537,
    # extract the telegram id from the argument starting with "ref_"
    referrer_id = None
    if context.args and len(context.args) > 0 and context.args[0].startswith("ref_"):
        print("DEBUG: Extracting referrer_id from context.args")
        try:
            referrer_id = int(context.args[0].split("_")[1])
            context.user_data['referrer_id'] = referrer_id
            print(f"DEBUG: Extracted referrer_id = {referrer_id}")
        except Exception as e:
            logger.error(f"Error extracting referrer_id: {e}")
    args = context.args  # this will be ["ref_123"] if link clicked

    print(f"DEBUG: args = {args}")

    # Check if user is already registered
    BACK_URL = get_bot_seetings().get("bot_url")
    try:
        url = f"{BACK_URL}/api/v1/users/{user_id}"
        user_exists = requests.get(url)
        telegram_id = user_exists.json().get("telegram_id", None)
        if telegram_id is not None:
            await update.effective_message.reply_text("Welcome back! You are already registered.")
            await update.effective_message.reply_text("Use /play to start playing the game!")
            return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error checking user existence: {e}")

    if args and len(args) > 0 and args[0].startswith("ref_"):      
        referrer_id = int(args[0].split("_")[1])
        context.user_data['referrer_id'] = referrer_id
        # get user profile from telegram using referrer id
        try:
            user_profile = await context.bot.get_chat(referrer_id)
            logger.info(f"user_profile = {user_profile}")
            await update.effective_message.reply_text(f"Welcome! You were referred by user {user_profile.username}")
        except Exception as e:
            logger.error(f"Error getting referrer profile: {e}")
            await update.effective_message.reply_text(f"Welcome! You were referred by user {referrer_id}")
   
        
        await update.effective_message.reply_text(text="Please share your phone number to complete registration.")
        contact_keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton(text="📞 Share Phone Number", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        await update.effective_message.reply_text(text="Tap the button below to share your phone number.", reply_markup=contact_keyboard)
        print("DEBUG: Returning REGISTER state for referred user")
        return REGISTER
    else:
        
        
        await update.effective_message.reply_text("Please share your phone number to complete registration.")
        contact_keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton(text="📞 Share Phone Number", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        await update.effective_message.reply_text(text="Tap the button below to share your phone number.", reply_markup=contact_keyboard)
        print("DEBUG: Returning REGISTER state for regular user")
        return REGISTER



async def redeem_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Redeem bonus for betting 10 consecutive games
    Awards 20 birr bonus if user has bet 10 consecutive games
    """
    telegram_id = update.effective_user.id
    BACK_URL = get_bot_seetings().get("bot_url")
    
    try:
        # Get user
        if LOCAL_MODE:
            user = await get_user_by_telegram_id(telegram_id)
            if not user:
                await update.message.reply_text(get_text(telegram_id, 'user_not_found'))
                return ConversationHandler.END
        else:
            user_response = requests.get(f'{BACK_URL}/api/v1/users/{telegram_id}')
            if user_response.status_code != 200:
                await update.message.reply_text(get_text(telegram_id, 'user_not_found'))
                return ConversationHandler.END
            user_data = user_response.json()
        
        # Get consecutive games bet count
        consecutive_games = user.consecutive_games_bet if LOCAL_MODE else user_data.get('consecutive_games_bet', 0)
        
        if consecutive_games >= 10:
            # User is eligible for bonus
            bonus_amount = 20.00
            
            # Add bonus to wallet
            if LOCAL_MODE:
                wallet = await get_user_wallet(user)
                bonus_decimal = Decimal(str(bonus_amount))
                wallet.balance = Decimal(str(wallet.balance)) + bonus_decimal
                await sync_to_async(wallet.save)()
                
                # Reset consecutive games counter
                user.consecutive_games_bet = 0
                user.last_bonus_redeemed_at = timezone.now()
                await sync_to_async(user.save)()
            else:
                # Call API to add bonus
                bonus_response = requests.post(
                    f'{BACK_URL}/api/v1/wallet/add-bonus/',
                    json={'telegram_id': telegram_id, 'amount': bonus_amount}
                )
                
                if bonus_response.status_code == 200:
                    # Reset consecutive games counter via API
                    requests.post(
                        f'{BACK_URL}/api/v1/users/reset-consecutive-games/',
                        json={'telegram_id': telegram_id}
                    )
            
            message = get_text(telegram_id, 'bonus_earned').format(
                amount=bonus_amount,
                games=consecutive_games
            )
        else:
            # User needs more games
            games_needed = 10 - consecutive_games
            message = get_text(telegram_id, 'bonus_progress').format(
                current=consecutive_games,
                needed=games_needed
            )
        
        await update.message.reply_text(message)
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Error in redeem_command: {e}")
        await update.message.reply_text(get_text(telegram_id, 'error_occurred'))
        return ConversationHandler.END


def main() -> None:
    BOT_TOKEN = get_bot_seetings().get("bot_token")
    application = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
 

    conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button), CommandHandler('register', register_command), CommandHandler('start', start)],
        states={
            # get_deposit_amount
            DEPOSIT_AMOUNT          : [MessageHandler(filters.TEXT & ~filters.COMMAND, deposit_amount)],
            GET_WITHDRAW_ACCOUNT    : [MessageHandler(filters.TEXT & ~filters.COMMAND, get_withdraw_account)],
            WITHDRAW_AMOUNT_CONFIRM : [MessageHandler(filters.TEXT & ~filters.COMMAND, get_withdraw_amount)],
            GET_TRANSCATION_DETAILS  : [MessageHandler(filters.TEXT & ~filters.COMMAND, get_transcation_details)],
            REGISTER                : [MessageHandler(filters.CONTACT, handle_phone)],
            WAIT_FOR_PAYMENT        : [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_payment)],
            SOME_STATE              : [CallbackQueryHandler(button)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    application.add_handler(CommandHandler('play', play_command))
    application.add_handler(CommandHandler('instructions', instruction_command))
    application.add_handler(CommandHandler('support', support_command))
    application.add_handler(CommandHandler('withdraw', withdraw_command))
    application.add_handler(CommandHandler('check_balance', check_balance_command))
    application.add_handler(CommandHandler('deposit', deposit_command))
    application.add_handler(CommandHandler('show_id', show_id_command))
    application.add_handler(CommandHandler('redeem', redeem_command))
    application.add_handler(CommandHandler('leaderboard', leaderboard_command))
    application.add_handler(conversation_handler)
    application.add_handler(CommandHandler('invite', handle_invite))  
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

async def cancel(update, context):
    await update.message.reply_text("Conversation cancelled. You can start again anytime.")
    return ConversationHandler.END