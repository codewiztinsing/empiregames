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
from utils import initialize_payment,get_bot_seetings,initialize_manual_session,get_user_phone,get_user_phone
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
from utils.helpers import daily_withdraw_limit,numnber_of_game_played,number_of_game_won,is_deposited_player,verify_receipt
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
        [InlineKeyboardButton("🔗 Join Group", url='https://t.me/wowbingos')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    # https://t.me/bilanbingobot?start=1464395537
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
    await update.message.reply_text('Welcome to Wow  Bingo! Select an option:', reply_markup=reply_markup)
    context.job_queue.run_once(conversation_timeout, CONVERSATION_TIMEOUT, chat_id=update.effective_chat.id)
    return SOME_STATE


# Function to create the play options keyboardF
def play_options_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🎮 Play 10", callback_data='10'),
         InlineKeyboardButton("🎮 Play 20", callback_data='20')],
        # [InlineKeyboardButton("🎮 Play 50", callback_data='50'),
        #  InlineKeyboardButton("🎮 Play 100", callback_data='100')],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]
    ]
    return InlineKeyboardMarkup(keyboard)



async def get_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
   
    await update.message.reply_text("Please enter the amount you want to withdraw:")
    return WITHDRAW_AMOUNT_CONFIRM

def deposit_opitions_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
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
        await update.message.reply_text("Please wait message from CBE/Telebirr. Your withdrawal will be processed within 30 minutes.")
        return ConversationHandler.END
    except Exception as e:
        print(f"Error sending message to user: {e}")



  


async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = play_options_keyboard() 
    user_id = update.effective_user.id
    username = update.effective_user.username
    try:
        BACK_URL = get_bot_seetings().get("bot_url")
        logger.info(f"Back url {BACK_URL}")
        res = requests.get(f'{BACK_URL}/api/v1/wallet/player/{user_id}')
        logger.info(f"Res {res}")
        if res.status_code == 200:
            balance = res.json().get('balance', 0)
            logger.info(f"User {username} balance: {balance}")
        else:
            balance = 0
            logger.error(f"Failed to get balance for user {username}")
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


# Function to create the play options keyboard
def support_options_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📞 Support 1",  url='https://t.me/@Wowbingosupport1')],
        [InlineKeyboardButton("📞 Support 2",  url='https://t.me/@Wowbingosupport2')],
        [InlineKeyboardButton("📞 Support 3",  url='https://t.me/IToffice1')],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data='menu')]
    ]
    return InlineKeyboardMarkup(keyboard)



async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = support_options_keyboard()
    await update.message.reply_text("Contact us using support button. We will respond to your message as soon as possible.", reply_markup=reply_markup)



async def instruction_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = instructions_options_keyboard()  # Create the inline keyboard
    await update.message.reply_text("Choose a instruction option:", reply_markup=reply_markup)




async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    BACK_URL = get_bot_seetings().get("bot_url")
    username = query.from_user.username 
    await query.answer()
  

    try:
        if query.data in ['10', '20', '50', '100']:
            user_id = query.from_user.id
            print("user_id = ",user_id)
            print("url = ",f'{BACK_URL}/api/v1/users/{user_id}')
            
            # Check if user is registered
            response = requests.get(f'{BACK_URL}/api/v1/users/{user_id}')
            print("response = ",response)
            logger.info(f"Response {response}")
            data = response.json()
            logger.info(f"Data {data}")
            print("data = ",data.get('phone'))
            if data.get('phone') is None:
                await query.edit_message_text(
                    text="You need to register first before playing. Use the /register command.",
                    reply_markup=instructions_options_keyboard()
                )
                return

            # Check user's balance
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
            web_app_url = f"{BACK_URL}?playerId={player_id}&betAmount={bet_amount}&playerName={query.from_user.username}"
            
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


        elif query.data.startswith('chapa_telebirr'):
            context.user_data['bank_id'] = 'Telebirr'
            phone_number = get_user_phone(query.from_user.id)
            print("phone_number = ",phone_number)
            deposit_amount =  context.user_data.get("deposit_amount",0)
            first_name = query.from_user.first_name or query.from_user.username
            last_name = query.from_user.last_name or query.from_user.username
            paymentMethod = 'telebirr'
            initialize_chapa_direct_charges(phone_number,deposit_amount,generate_tx_ref(),first_name,last_name,paymentMethod)
            return ConversationHandler.END

        elif query.data.startswith('chapa_cbe'):
            context.user_data['bank_id'] = 'CBE'
            phone_number = get_user_phone(query.from_user.id)
            print("phone_number = ",phone_number)
            deposit_amount =  context.user_data.get("deposit_amount",0)
            first_name = query.from_user.first_name or query.from_user.username
            last_name = query.from_user.last_name or query.from_user.username
            paymentMethod = 'cbe'
            initialize_chapa_direct_charges(phone_number,deposit_amount,generate_tx_ref(),first_name,last_name,paymentMethod)
            return ConversationHandler.END


        elif query.data == 'withdraw_confirm':
            return WITHDRAW_AMOUNT_CONFIRM

        if query.data == 'play' :
            await query.edit_message_text(
                text="Choose a play option:",
                reply_markup=play_options_keyboard()
            )

        elif query.data == 'contact_support':
            await query.edit_message_text(
                text="Choose a contact support:",
                reply_markup=support_options_keyboard()
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
           
           

            # Create payment summary with user details
            payment_summary = (
                    "🏦 TELE BIRR STATEMENT\n" +
                    f"💰  {balance} Birr\n" +
                    f"👥  {first_name} \n" +
                    f"📄 Transaction ID: {telegram_id}\n" +
                    f"🔙 Back to Menu\n" 
                ) 
            await query.edit_message_text(text=payment_summary)
            return

        
                
        

        elif query.data in ['10','20']:

            player_id = query.from_user.id
            user_id = query.from_user.id
            username = query.from_user.username or query.from_user.first_name
            bet_amount = query.data
        
            _resp_u = requests.get(f'{BACK_URL}/users/{user_id}/')
            wallet_amount = (_resp_u.json().get('balance',0)) if _resp_u.headers.get('content-type','').startswith('application/json') else 0
            print("wallet_amount = ",wallet_amount)

            web_app_url = (
                f"https://wowliyubingo.com/?playerId={player_id}&name={username}&betAmount={bet_amount}&wallet_amount={wallet_amount}"
            )

            keyboard = [
                [InlineKeyboardButton("Open Wow Bingo!", web_app=WebAppInfo(url=web_app_url))]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.message.reply_text("Start playing Wow bingo", reply_markup=reply_markup)

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
                "return_url":f"https://t.me/wowbingobotbotbot",
                "customization":{
                    "title": "Wow Bingo",
                    "description": "Deposit to Wow Bingo",
                    "logo": "https://wowliyubingo.com/static/media/logo.png"
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
           
        elif query.data == "addispay":
            BACK_URL = get_bot_seetings().get("bot_url")
            # check if user is registered
            response = requests.get(f"{BACK_URL}/api/v1/users/{query.from_user.id}")
            user_from_api = response.json() if response.headers.get('content-type','').startswith('application/json') else {}            
            if not user_from_api.get("success", False):
                await query.edit_message_text(text="You need to register first. Use the /register command.")
                return ConversationHandler.END
                
            phone_number = user_from_api.get("phone")
            tax_ref = generate_tx_ref()
            addis_session = create_session(
            float(context.user_data['deposit_amount']), 
            "ETB",
            f"{query.from_user.username}@gmail.com", 
            query.from_user.first_name,
             query.from_user.last_name,
            phone_number, 
            tax_ref, 
            f"{BACK_URL}/api/v1/wallet/webhook/addispay/callback/",
             "https://wowliyubingo.com/success", {
                "title": "Wow Bingo",
                "description": "Deposit to Wow Bingo",
                "logo": "https://wowliyubingo.com/static/media/logo.png"
            })
            if addis_session.get("status") == "success":
                data = addis_session.get("data")
                # create session in database
                session_data = {
                    "amount": float(context.user_data['deposit_amount']),
                    "currency": "ETB",
                    "email": f"{query.from_user.username}@gmail.com",
                    "first_name": query.from_user.first_name or "User",
                    "last_name": query.from_user.last_name or "Name",
                    "phone_number": phone_number,
                    "tx_ref": tax_ref,
                    "callback_url": f"{BACK_URL}/api/v1/wallet/webhook/addispay/callback/",
                    "session_id": data.get("uuid")
                }
                print("session_data = ",session_data)
                session_creating_response = requests.post(f"{BACK_URL}/api/v1/wallet/addispay/create-session", json=session_data)
                if session_creating_response.status_code == 200:
                    checkout_url = data.get("checkout_url") + "/" + data.get("uuid")
                else:
                    await query.edit_message_text(text="Failed to create payment session. Please try again.")
                    return ConversationHandler.END
            else:
                await query.edit_message_text(text="An error occurred. Please try again.")
                return ConversationHandler.END
            keyboard = [
                [InlineKeyboardButton("Pay with AddisPay", url=checkout_url)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="Click the button below to complete your payment:",
                reply_markup=reply_markup
            )

            return ConversationHandler.END
           

      

        elif query.data == 'withraw_with_chapa':
            await query.edit_message_text(
                text="how much do you want to withdraw?"
            )
            context.user_data['withdraw_amount'] = query.data
            context.user_data['payment_method'] = 'chapa'
            return DEPOSIT_AMOUNT
            # return ConversationHandler.END

          
            
            
        
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
            await query.edit_message_text(text="📱 Please share your phone number to register:")
            await query.message.reply_text(
                text="Tap the button below to share your phone number.",
                reply_markup=contact_keyboard
            )
            return REGISTER

        elif query.data == 'manual':
            keyboard = [
                [InlineKeyboardButton("Telebirr", callback_data='manual_telebirrcc')]
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
                 InlineKeyboardButton("Check Balance", callback_data='check_balance')],
                [InlineKeyboardButton("Deposit", callback_data='deposit'),
                 InlineKeyboardButton("Register", callback_data='register_menu')]

              
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Welcome to Wow Bingo! Please select an option:", reply_markup=reply_markup)
            
            
 
        else:

            keyboard = [
                [InlineKeyboardButton("Play Game", callback_data='play'),
                 InlineKeyboardButton("Check Balance", callback_data='check_balance')],
                [InlineKeyboardButton("Deposit", callback_data='deposit'),
                 InlineKeyboardButton("Register", callback_data='register_menu')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Welcome to Wo w Bingo! Please select an option:", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error handling query: {query.data} - {e}")
        await query.edit_message_text(text="An error occurred. Please try again.")

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
        [
                # InlineKeyboardButton("Chapa", callback_data='chapa'),
                InlineKeyboardButton("Telebirr", callback_data='chapa_telebirr'),
                InlineKeyboardButton("CBE", callback_data='chapa_cbe')

            # InlineKeyboardButton("AddisPay", callback_data='addispay')
        ],
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
        "start", 
        "start the bot"
    ),

    BotCommand(
        "play", 
        "start playing"
        ),

    BotCommand(
        "instructions", 
        "instructions to play game"
        ),

      BotCommand(
        "support", 
        "Contact us"
        ),

    BotCommand(
        "withdraw", 
        "withdraw funds"
        ),
    BotCommand(
        "invite", 
        "Invite your friends"
        )
    ]


async def post_init(app):
    await app.bot.set_my_commands(all_public_commands_descriptions)


      
  

async def handle_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    BACK_URL = get_bot_seetings().get("bot_url")
    # Check if user is registered
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

    invite_link = f"https://t.me/wowbingobot?start={user_id}"
    
    message = (
        f"🎮 Invite your friends to Wow Bingo!\n\n"
        f"Share this link with your friends:\n{invite_link}\n\n"
        f"Your current balance: {balance} ETB\n\n"
        f"Invite friends and enjoy playing together! 🎲"
    )

    # Add 20 ETB bonus for inviting
    requests.post(f'{BACK_URL}/api/v1/wallet/player/{user_id}/', json={
        'user_id': user_id,
        'amount': 20
    })
    
    await update.message.reply_text(message)



async def handle_manual_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import uuid
    payment_method = context.user_data['payment_method']
    if payment_method == 'manual_telebirr':
        message = update.message.text
        amount = context.user_data['deposit_amount']
        session_id = f"{uuid.uuid4()}"
        user_id = update.effective_user.id
        BACK_URL = get_bot_seetings().get("bot_url")
        
        # Get user phone from database
        response = requests.get(f'{BACK_URL}/api/v1/users/{user_id}')
        if response.status_code == 200:
            user_data = response.json()
            phone_number = user_data.get('phone', '')
            initialize_manual_session(amount, session_id, phone_number,message)
            return ConversationHandler.END
        else:
            await update.message.reply_text("An error occurred. Please try again.")
            return ConversationHandler.END
        await update.message.reply_text("Telebirr payment received. Please wait for verification.")
    elif payment_method == 'manual_cbe':
        message = update.message.text
        await update.message.reply_text("CBE payment received. Please wait for verification.")

def main() -> None:
    BOT_TOKEN = get_bot_seetings().get("bot_token")
    application = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
 

    conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button)],
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

  
 

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('play', play_command))
    application.add_handler(CommandHandler('instructions', instruction_command))
    application.add_handler(CommandHandler('support', support_command))
    application.add_handler(CommandHandler('withdraw', withdraw_command))
    application.add_handler(conversation_handler)
    application.add_handler(CommandHandler('invite', handle_invite))  
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

async def cancel(update, context):
    await update.message.reply_text("Conversation cancelled. You can start again anytime.")
    return ConversationHandler.END