import json
import requests
import logging
import random
import string
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
from utils import initialize_payment,get_bot_seetings,get_user_phone,get_user_phone
from utils.chapa import transfer_funds,get_available_banks,initialize_chapa_direct_charges   
from utils.addis import create_session
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler,
)
from utils.helpers import daily_withdraw_limit,numnber_of_game_played,number_of_game_won,is_deposited_player,get_game_type
from utils.factory import handle_manual_payment
from datetime import datetime
from telegram import BotCommand
from register import *



logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)




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
    keyboard = [
        [InlineKeyboardButton("🎮 Play", callback_data='play'),
         InlineKeyboardButton("📝 Register",callback_data = "register")],
        [InlineKeyboardButton("💰 Check Balance", callback_data='check_balance'),
         InlineKeyboardButton("💳 Deposit", callback_data='deposit')],
        [InlineKeyboardButton("📞 Contact Support", callback_data='contact_support'),
         InlineKeyboardButton("📚 Instruction", callback_data='instructions')],
        # [InlineKeyboardButton("🔗 Join Group", url='https://t.me/wowbingos')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    # https://t.me/akerbingobot?start=1464395537
    # Extract referral info from deep link if present
    referrer_id = None
    if context.args and len(context.args) > 0:
        try:
            referrer_id = int(context.args[0])
            print("referrer_id = ",referrer_id)

            # Store referrer ID in user data for later use
            context.user_data['referrer_id'] = referrer_id
        except ValueError:
            logger.warning(f"Invalid referrer ID format: {context.args[0]}")
    await update.message.reply_text('Welcome to Aker Bingo! Select an option:', reply_markup=reply_markup)
    context.job_queue.run_once(conversation_timeout, CONVERSATION_TIMEOUT, chat_id=update.effective_chat.id)
    return SOME_STATE


# Function to create the play options keyboardF
def play_options_keyboard(update: Update) -> InlineKeyboardMarkup:
    game_types_response = get_game_type()
    game_types = game_types_response.get('game_types', []) if game_types_response else []
    logger.info(f"game_types = {game_types}")
    keyboard = []
    for game_type in game_types:
        keyboard.append([InlineKeyboardButton(f"🎮 Play {game_type['bet_amount']}", web_app=WebAppInfo(url=f"https://akerbingo.com/?playerId={update.effective_user.id}&betAmount={game_type['bet_amount']}&playerName={update.effective_user.username}"))])
    keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data='back')])
    return InlineKeyboardMarkup(keyboard)



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
    banks = get_available_banks()
    logger.info("banks = ",banks)
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
    # Get user's wallet balance
    telegram_id = update.effective_user.id
    BACK_URL = get_bot_seetings().get("bot_url")

    logger.info(f"Back url {BACK_URL}")
    logger.info(f"telegram_id {telegram_id}")
    logger.info(f"amount {amount}")
 
    try:
        _resp = requests.get(f'{BACK_URL}/api/v1/wallet/player/{telegram_id}')
        wallet_response = _resp.json() if _resp.headers.get('content-type','').startswith('application/json') else {}
        balance = float(wallet_response.get('balance', 0))


        daily_limit = daily_withdraw_limit(telegram_id)
        logger.info(f"daily_withdraw_limit {daily_limit}")
        if int(daily_limit) > 3:
            await update.message.reply_text(f"You have reached the daily withdraw limit. Please try again tomorrow.")
            return WITHDRAW_AMOUNT_CONFIRM
        is_deposited = is_deposited_player(telegram_id)
        if not is_deposited:
            await update.message.reply_text(f"You need to deposit first. 20 ETB minimum deposit is required to withdraw.")
            return WITHDRAW_AMOUNT_CONFIRM

 

        number_game_played = numnber_of_game_played(telegram_id)
        number_game_won = number_of_game_won(telegram_id)

        if int(number_game_played) < 5:
            await update.message.reply_text(f"ከ 5 ጨወታ በላይ መጫዎት አለብዎት")
            return WITHDRAW_AMOUNT_CONFIRM

        # if int(number_game_won) < 2:
        #     await update.message.reply_text(f"2 ጨወታ ማሽነፍ አለብዎት")
        #     return WITHDRAW_AMOUNT_CONFIRM

        if int(amount) > 100:
            await update.message.reply_text(f"Withdrawal amount must be less than 100 ETB")
            return WITHDRAW_AMOUNT_CONFIRM

       
        if int(balance) < 20:
            await update.message.reply_text(f"You must leave at least 20 ETB in your wallet. Please enter a smaller amount.")
            return WITHDRAW_AMOUNT_CONFIRM


        if int(amount) < 50:
            await update.message.reply_text(f"Withdrawal amount must be at least 50 ETB")
            return WITHDRAW_AMOUNT_CONFIRM

        
        # Check if withdrawal amount exceeds balance
        if int(amount) > int(balance):

            await update.message.reply_text(f"Insufficient funds. Your current balance is {balance} ETB")
            return WITHDRAW_AMOUNT_CONFIRM

        else:
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
    BACK_URL = get_bot_seetings().get("bot_url")
    try:
        withdraw_amount = float(context.user_data['withdraw_amount'])
        bank_id = context.user_data['bank_id']
        banks_to_bank_id = context.user_data['banks_to_bank_id']
        bank_id = banks_to_bank_id.get(f"{bank_id}".title())
        transfer_funds(f"{update.effective_user.first_name} {update.effective_user.last_name}", account_number, withdraw_amount, "ETB", generate_tx_ref(), bank_id)
        await update.message.reply_text("Please wait message from CBE/Aker. Your withdrawal will be processed within 30 minutes.")
        return ConversationHandler.END
    except Exception as e:
        print(f"Error sending message to user: {e}")



async def get_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username
    BACK_URL = get_bot_seetings().get("bot_url")
    res = requests.get(f'{BACK_URL}/api/v1/wallet/player/{user_id}')
    balance = res.json().get('balance', 0)
    return balance


async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = play_options_keyboard(update) 
    balance = get_balance(update, context)
    try:
        BACK_URL = get_bot_seetings().get("bot_url")
        logger.info(f"Back url {BACK_URL}")
        res = requests.get(f'{BACK_URL}/api/v1/wallet/player/{update.effective_user.id}')
        logger.info(f"Res {res}")
        if res.status_code == 200:
            balance = res.json().get('balance', 0)
            logger.info(f"User {update.effective_user.username} balance: {balance}")
        else:
            balance = 0
            logger.error(f"Failed to get balance for user {update.effective_user.username}")
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
        game_types_response = get_game_type()
        game_types = game_types_response.get('game_types', []) if game_types_response else []
        if query.data in ['10', '20', '50', '100'] or query.data in [str(game_type['bet_amount']) for game_type in game_types]:
            user_id = query.from_user.id
            response = requests.get(f'{BACK_URL}/api/v1/users/{user_id}')
            logger.info(f"Response {response}")
            data = response.json()
            logger.info(f"Data {data}")
            if data.get('phone') is None:
                await query.edit_message_text(
                    text="You need to register first before playing. Use the /register command.",
                    reply_markup=instructions_options_keyboard()
                )
                return
            bet_amount = int(query.data)
            wallet_response = requests.get(f'{BACK_URL}/api/v1/wallet/player/{user_id}')
            wallet_data = wallet_response.json()
            balance = wallet_data.get('balance', 0)
           
          
            if balance < bet_amount:
                await query.edit_message_text(
                    text=f"Insufficient balance. Your current balance is {balance} ETB. Please deposit more to play.",
                    reply_markup=deposit_opitions_keyboard()
                )
                return

            player_id = query.from_user.id
            web_app_url = f"https://akerbingo.com/?playerId={player_id}&betAmount={bet_amount}&playerName={query.from_user.username}"
            
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
        if query.data == 'play' :
            await query.edit_message_text(
                text="Choose a play option:",
                reply_markup=play_options_keyboard(update)
            )

        elif query.data == 'contact_support':
            # redirect user to @AkerBingo
            await query.edit_message_text(
                text="Contact us using support button",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📞 Support",  url='https://t.me/AkerBingo')]])
            )
            return


          
        
        elif query.data == 'instructions':
            await query.edit_message_text(
                text="Choose an instruction option:",
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
            BACK_URL = get_bot_seetings().get("bot_url") 
            username = query.from_user.username
            first_name = query.from_user.first_name
            last_name = query.from_user.last_name
            telegram_id = query.from_user.id
            print("BACK_URL = ",f"{BACK_URL}/api/v1/wallet/player/{telegram_id}")
            response = requests.get(f'{BACK_URL}/api/v1/wallet/player/{telegram_id}')
            print("response = ",response)
            balance = response.json().get('balance',0)
            
            # Get user info and game statistics
            user_response = requests.get(f'{BACK_URL}/api/v1/users/{telegram_id}/')
            user_data = user_response.json() if user_response.headers.get('content-type','').startswith('application/json') else {}
            games_played_this_week = user_data.get('games_played_this_week', 0)
            
            # Calculate remaining games needed
            remaining_games = max(0, 27 - games_played_this_week)
            
            # Create payment summary with user details and weekly progress
            payment_summary = (
                    "🏦 Aker BINGO STATEMENT\n" +
                    f"💰  {balance} Birr\n" +
                    f"👥  {first_name} \n" +
                    f"📄 Transaction ID: {telegram_id}\n\n" +
                    f"🎮 Weekly Games Progress:\n" +
                    f"📊 Games Played This Week: {games_played_this_week}/27\n" +
                    f"⏳ Games Remaining: {remaining_games} games\n" +
                    f"🔙 Back to Menu\n" 
                ) 
            await query.edit_message_text(text=payment_summary)
            return
        elif query.data in ['10','20']:
            player_id = query.from_user.id
            user_id = query.from_user.id
            username = query.from_user.username or query.from_user.first_name
            bet_amount = int(query.data)
            
            # Check if user is registered
            response = requests.get(f'{BACK_URL}/api/v1/users/{user_id}')
            data = response.json()
            if data.get('phone') is None:
                await query.edit_message_text(
                    text="You need to register first before playing. Use the /register command.",
                    reply_markup=instructions_options_keyboard()
                )
                return
            
            # Check wallet balance
            _resp_u = requests.get(f'{BACK_URL}/api/v1/wallet/player/{user_id}')
            wallet_data = _resp_u.json() if _resp_u.headers.get('content-type','').startswith('application/json') else {}
            balance = wallet_data.get('balance', 0)
            
            # Check if balance is sufficient
            if balance < bet_amount:
                await query.edit_message_text(
                    text=f"Insufficient balance. Your current balance is {balance} ETB. Please deposit more to play.",
                    reply_markup=deposit_opitions_keyboard()
                )
                return
            
            web_app_url = (
                f"https://akerbingo.com/?playerId={player_id}&name={username}&betAmount={bet_amount}&wallet_amount={balance}"
            )

            keyboard = [
                [InlineKeyboardButton("Open Aker Bingo!", web_app=WebAppInfo(url=web_app_url))]
                # [InlineKeyboardButton("Open Wow Bingo!", url=web_app_url)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.message.reply_text("Start playing Aker bingo", reply_markup=reply_markup)

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

        elif query.data == "chapa":
            BACK_URL = get_bot_seetings().get("bot_url")
            url = "/api/v1/wallet/chapa/create-session"
            full_url = f"{BACK_URL}{url}"
            

            _ufa = requests.get(f"{BACK_URL}/api/v1/users/{query.from_user.id}")
            user_from_api = _ufa.json() if _ufa.headers.get('content-type','').startswith('application/json') else {}
            phone_number = user_from_api.get("phone")
           
            data = {
                "amount": context.user_data['deposit_amount'],
                "currency": "ETB",
                "first_name": query.from_user.first_name,
                "last_name": query.from_user.last_name or query.from_user.username,
                "email": f"{query.from_user.username}@gmail.com",
                "phone_number": phone_number,
                "tx_ref":generate_tx_ref(),
                "return_url":f"https://t.me/akerbingobotbotbot",
                "customization":{
                    "title": "Aker Bingo",
                    "description": "Deposit to Aker Bingo",
                    "logo": "https://akerbingo.com/static/media/logo.png"
                },
                # "callback_url": "https://webhook.site/6bca0770-2235-4096-b8f6-41b861ec40e9"
                "callback_url": f"{BACK_URL}/api/v1/wallet/webhook/chapa/callback/"
            }

            response = requests.post(full_url, json=data)
            logger.info(f"response = {response}")
            if response.status_code == 200:
                chapa_session = initialize_payment(**data)
                logger.info(f"data = {chapa_session}")

                data = chapa_session.get("data")
            
                checkout_url = data.get("checkout_url")
                keyboard = [
                    [InlineKeyboardButton("Pay with Chapa", url=checkout_url)]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    text="Click the button below to complete your payment:",
                    reply_markup=reply_markup
                )

                return ConversationHandler.END

            else:
                await query.edit_message_text(text="An error occurred. Please try again.")
                return ConversationHandler.END
    
 
        
        elif query.data == 'cancel':
            await query.edit_message_text(text="Withdrawal request cancelled.")
            return ConversationHandler.END


        
        elif query.data == "register":
            # Use a ReplyKeyboardMarkup with request_contact to actually receive phone number
            contact_keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton(text="📞 Share Phone Number", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            # get notice message from file notice_message.txt
            with open('notice.txt', 'r') as file:
                notice_message = file.read()
            await query.edit_message_text(text=notice_message)
            # await query.edit_message_text(text="📱 Please share your phone number to register:")
            await query.message.reply_text(
                text="Tap the button below to share your phone number.",
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
            await query.edit_message_text(text=message, parse_mode=ParseMode.HTML)
            return WAIT_FOR_PAYMENT

        elif query.data == "manual_cbe":
            filepath = "cbe_message.html"
            with open(filepath, 'r') as file:
                message = file.read()
            await query.edit_message_text(text=message, parse_mode=ParseMode.HTML)
            context.user_data['payment_method'] = 'manual_cbe'
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
            await query.edit_message_text("Welcome to Aker Bingo! Please select an option:", reply_markup=reply_markup)
            
            
 
        else:

            keyboard = [
                [InlineKeyboardButton("Play Game", callback_data='play'),
                 InlineKeyboardButton("Check Balance", callback_data='check_balance')],
                [InlineKeyboardButton("Deposit", callback_data='deposit'),
                 InlineKeyboardButton("Register", callback_data='register_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Welcome to Aker Bingo! Please select an option:", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error handling query: {query.data} - {e}")
        await query.edit_message_text(text="An error occurred. Please try again.")


async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Contact us using support button", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📞 Support",  url='https://t.me/AkerBingo')]]))
    return ConversationHandler.END

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
        )
    ]


async def post_init(app):
    await app.bot.set_my_commands(all_public_commands_descriptions)


      
  

async def handle_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    BACK_URL = get_bot_seetings().get("bot_url")
    user_id = update.effective_user.id
    referrer_id = context.user_data.get('referrer_id')
    logger.info(f"referrer_id = {referrer_id}")

    response = requests.get(f'{BACK_URL}/api/v1/users/{user_id}')
    if response.status_code != 200:
        await update.message.reply_text(
            "You need to register first before inviting others. Use the /register command."
        )
        return

    # Get user's wallet balance
    _wr = requests.get(f'{BACK_URL}/api/v1/wallet/player/{user_id}/')
    wallet_response = _wr.json() if _wr.headers.get('content-type','').startswith('application/json') else {}
    balance = wallet_response.get('balance', 0)

    # Instead of a URL button, use a "Forward" button that triggers a callback for forwarding the referral message.
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Share", switch_inline_query=f"ref_{user_id}")]
    ])
    
    message = (
        "here is referral link:"
    )
  
    await update.message.reply_text(text=message, reply_markup=reply_markup)



async def register_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("DEBUG: register_command function called")
    user_id = update.effective_user.id
    BACK_URL = get_bot_seetings().get("bot_url")
    
    # Check if user is already registered
    response = requests.get(f'{BACK_URL}/api/v1/users/{user_id}')
    if response.status_code == 200:
        user_data = response.json()
        if user_data.get('phone'):
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
            # get notice message from file notice_message.txt
    with open('notice.txt', 'r') as file:
                notice_message = file.read()
    await update.message.reply_text(text=notice_message)
    await update.message.reply_text(
                text="Tap the button below to share your phone number.",
                reply_markup=contact_keyboard
            )
    return REGISTER

async def check_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    BACK_URL = get_bot_seetings().get("bot_url")
    telegram_id = update.effective_user.id
    wallet_response = requests.get(f'{BACK_URL}/api/v1/wallet/player/{telegram_id}')
    wallet_data = wallet_response.json() if wallet_response.headers.get('content-type','').startswith('application/json') else {}
    balance = wallet_data.get('balance', 0)
    
    # Get user info and game statistics
    user_response = requests.get(f'{BACK_URL}/api/v1/users/{telegram_id}/')
    user_data = user_response.json() if user_response.headers.get('content-type','').startswith('application/json') else {}
    games_played_this_week = user_data.get('games_played_this_week', 0)
    
    # Get user info for personalization
    user_name = update.effective_user.first_name or update.effective_user.username or "Player"
    
    # Calculate remaining games needed
    remaining_games = max(0, 27 - games_played_this_week)
    
    # Create appealing balance message
    if balance > 0:
        message = (
        f"💰 Hey {user_name}! Your Current Account Balance!\n"
        f"👤 **Name:** {user_name}\n"
        f"📱 **Phone Number:** {telegram_id}\n"
        f"💵 **Withdrawable Balance:** {balance} ETB\n"
        f"🔒 **Non-Withdrawable Balance:** 0.0 ETB\n"
        f"🎯 **Total Balance:** {balance} ETB\n\n"
        f"🎮 **Weekly Games Progress:**\n"
        f"📊 **Games Played This Week:** {games_played_this_week}/27\n"
        f"⏳ **Games Remaining:** {remaining_games} games to complete weekly requirement\n\n"
        f"🎮 Ready to play? Your balance looks great!"
        )
    else:
        message = (
        f"💰 Hey {user_name}! Your Current Account Balance!\n"
        f"👤 **Name:** {user_name}\n"
        f"📱 **Phone Number:** {telegram_id}\n"
        f"💵 **Withdrawable Balance:** {balance} ETB\n"
        f"🔒 **Non-Withdrawable Balance:** 0.0 ETB\n"
        f"🎯 **Total Balance:** {balance} ETB\n\n"
        f"🎮 **Weekly Games Progress:**\n"
        f"📊 **Games Played This Week:** {games_played_this_week}/27\n"
        f"⏳ **Games Remaining:** {remaining_games} games to complete weekly requirement\n\n"
        f"💳 Please deposit to start playing and complete your weekly games!"
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
        
        # show notice
        try:
            with open('notice.txt', 'r') as file:
                notice_message = file.read()
            await update.effective_message.reply_text(text=notice_message)
        except Exception as e:
            logger.error(f"Error reading notice file: {e}")
        
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
        #show notice
        try:
            with open('notice.txt', 'r') as file:
                notice_message = file.read()
            await update.effective_message.reply_text(text=notice_message)
        except Exception as e:
            logger.error(f"Error reading notice file: {e}")
        await update.effective_message.reply_text("Please share your phone number to complete registration.")
        contact_keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton(text="📞 Share Phone Number", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        await update.effective_message.reply_text(text="Tap the button below to share your phone number.", reply_markup=contact_keyboard)
        print("DEBUG: Returning REGISTER state for regular user")
        return REGISTER



def main() -> None:
    BOT_TOKEN = get_bot_seetings().get("bot_token")
    application = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
 

    conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button), CommandHandler('register', register_command), CommandHandler('start', start_command)],
        states={
            # get_deposit_amount
            DEPOSIT_AMOUNT          : [MessageHandler(filters.TEXT & ~filters.COMMAND, deposit_amount)],
            GET_WITHDRAW_ACCOUNT    : [MessageHandler(filters.TEXT & ~filters.COMMAND, get_withdraw_account)],
            WITHDRAW_AMOUNT_CONFIRM : [MessageHandler(filters.TEXT & ~filters.COMMAND, get_withdraw_amount)],
            GET_TRANSCATION_DETAILS  : [MessageHandler(filters.TEXT & ~filters.COMMAND, get_transcation_details)],
            REGISTER                : [MessageHandler(filters.CONTACT, handle_phone)],
            WAIT_FOR_PAYMENT        : [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_payment)],
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
    application.add_handler(CommandHandler('withdraw', withdraw_command))
    application.add_handler(conversation_handler)
    application.add_handler(CommandHandler('invite', handle_invite))  
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

async def cancel(update, context):
    await update.message.reply_text("Conversation cancelled. You can start again anytime.")
    return ConversationHandler.END