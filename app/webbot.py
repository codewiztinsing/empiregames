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
from utils import initialize_payment,get_bot_seetings   
from utils.chapa import get_available_banks,transfer_funds
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ConversationHandler,
)
from datetime import datetime
from telegram import BotCommand
from register import *
from helpers import get_numbers_of_games_played



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
GET_DEPOSIT_AMOUNT,WITHDRAW_AMOUNT_CONFIRM,WITHDRAW_AMOUNT_CANCEL,CHOOSE_PAYMENT_METHOD,GET_WITHDRAW_ACCOUNT,GET_TRANSCATION_DETAILS = range(2,8)

CONVERSATION_TIMEOUT = 300  # 5 minutes




    
    


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
        [InlineKeyboardButton("🎮 Play 50", callback_data='50'),
         InlineKeyboardButton("🎮 Play 100", callback_data='100')],
        [InlineKeyboardButton("🎮 Play Demo", callback_data='play_demo'),
         InlineKeyboardButton("🔙 Back to Menu", callback_data='back')
         ],
    ]
    return InlineKeyboardMarkup(keyboard)



async def get_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
   
    await update.message.reply_text("Please enter the amount you want to withdraw:")
    return WITHDRAW_AMOUNT_CONFIRM

def deposit_opitions_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
              
                 [
                InlineKeyboardButton("🔙 Back to Menu", callback_data='menu')
 
                 ]
            ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def withdraw_opitions_keyboard(context: ContextTypes.DEFAULT_TYPE) -> InlineKeyboardMarkup:
    
    available_banks = get_available_banks().get("data",[])
    keyboard = []
    banks_to_bank_id = {}
    for bank in available_banks:
        # Create 4x4 grid of bank buttons
        bank_id = bank.get("id")
        bank_name = bank.get("name")
        banks_to_bank_id[bank_id] = bank_name
        keyboard.append([InlineKeyboardButton(bank_name, callback_data=f'withraw_with_{bank_id}')]) 
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
        logger.info(f"wallet url {BACK_URL}/api/v1/wallet/player/{telegram_id}")

        wallet_response = requests.get(f'{BACK_URL}/api/v1/wallet/player/{telegram_id}').json()
        balance = float(wallet_response.get('balance', 0))
        logger.info(f"balance {balance}")
      
        if int(balance) < 20:
            await update.message.reply_text(f"You must leave at least 20 ETB in your wallet. Please enter a smaller amount.")
            return WITHDRAW_AMOUNT_CONFIRM


        if int(amount) < 100:
            await update.message.reply_text(f"Withdrawal amount must be at least 100 ETB")
            return WITHDRAW_AMOUNT_CONFIRM

        game_played = get_numbers_of_games_played(telegram_id)
        logger.info(f"game_played {game_played}")

        if game_played < 5:
            await update.message.reply_text(f"You must play at least 5 games before withdrawing. Please play more games.")
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
            bank_name = banks_to_bank_id.get(int(context.user_data['bank_id']))
            logger.info(f"bank_name {bank_name}")
            logger.info(f"banks_to_bank_id {banks_to_bank_id}")
            logger.info(f"bank id  {context.user_data['bank_id']}")
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
        # deduct amount from user's balance
        res = requests.put(f'{BACK_URL}/api/v1/wallet/player/{update.effective_user.id}/', json={'amount': withdraw_amount,"action":"withdraw"})
        ###
        await update.message.reply_text("Withdrawal request sent to admin. Please wait for approval.")
        transfer_funds(f"{update.effective_user.first_name} {update.effective_user.last_name}", account_number, withdraw_amount, "ETB", generate_tx_ref(), context.user_data['bank_id'])
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
        [InlineKeyboardButton("📞 Support",  url='https://t.me/@wowliyu_bingo')],
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
            
            # Check if user is registered
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
            
           

        
        if query.data == 'play_demo':
            player_id = query.from_user.id
            username = query.from_user.username
            user_id = query.from_user.id
            bet_amount = 0  # Demo game has no bet amount
            wallet_amount = requests.get(f'{BACK_URL}/payments/wallet/{user_id}/').json().get('balance',0)
            web_app_url = (
                f"{BACK_URL}/?playerId={player_id}&name={username}&betAmount={bet_amount}&wallet_amount={wallet_amount}&demo=true"
            )

            await query.edit_message_text(
                text=f"Starting demo game...",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("Play Demo", web_app=WebAppInfo(url=web_app_url))
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

        
                
        

        elif query.data in ['10','20', '50','100']:

            player_id = query.from_user.id
            user_id = query.from_user.id
            username = query.from_user.username or query.from_user.first_name
            bet_amount = query.data
        
            wallet_amount = requests.get(f'{BACK_URL}/users/{user_id}/').json().get('balance',0)
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
            

            user_from_api = requests.get(f"{BACK_URL}/api/v1/users/{query.from_user.id}").json()
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
           

            keyboard = [
                [InlineKeyboardButton("Pay with Chapa", callback_data=session_id)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                text="Open Chapa to pay",
                reply_markup=reply_markup
            )

        elif query.data == 'withraw_with_chapa':
            await query.edit_message_text(
                text="how much do you want to withdraw?"
            )
            return WITHDRAW_AMOUNT_CONFIRM

          
            
            
        
        elif query.data == 'cancel':
            await query.edit_message_text(text="Withdrawal request cancelled.")
            return ConversationHandler.END


        
        elif query.data == "register":

           
            # return begin_register(update,context)
            await query.edit_message_text('Welcome! Use /register to start the registration process.')
          
        elif query.data == 'menu':
            keyboard = [
                [InlineKeyboardButton("Play Game", callback_data='play'),
                 InlineKeyboardButton("Check Balance", callback_data='check_balance')],
                [InlineKeyboardButton("Deposit", callback_data='deposit'),
                 InlineKeyboardButton("Register", callback_data='register')]

              
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Welcome to Wow Bingo! Please select an option:", reply_markup=reply_markup)
            
            
 
        else:

            keyboard = [
                [InlineKeyboardButton("Play Game", callback_data='play'),
                 InlineKeyboardButton("Check Balance", callback_data='check_balance')],
                [InlineKeyboardButton("Deposit", callback_data='deposit'),
                 InlineKeyboardButton("Register", callback_data='register')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Welcome to Wo w Bingo! Please select an option:", reply_markup=reply_markup)
    except Exception as e:
        logger.error(f"Error handling query: {query.data} - {e}")
        await query.edit_message_text(text="An error occurred. Please try again.")

async def deposit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    amount = update.message.text

    if float(amount) < 20:
        await update.message.reply_text("Minimum deposit amount is 20 ETB. Please enter a higher amount.")
        return DEPOSIT_AMOUNT

    back_url = get_bot_seetings().get("bot_url")
   
    full_url = f"{back_url}/api/v1/users/{update.effective_user.id}"
    logger.info(f"full_url = {full_url}")

    phone = requests.get(full_url).json().get("phone")
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
        [InlineKeyboardButton("Chapa", callback_data='chapa')]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    await update.message.reply_text(message,parse_mode=ParseMode.HTML,reply_markup=reply_markup)
    
   
  



async def get_transcation_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  
    message = update.message.text
    amount = parsed_data.get('amount')
    user_id = update.effective_user.id
    username = update.effective_user.username
    transaction_number = parsed_data.get('transaction_details')['id']

    print("transaction_number = ",transaction_number)
   
    response = requests.get(f'{BACK_URL}/transactions/transactionId/{transaction_number}')
    res = response.json()
    if res.get('status') == 'error':
        await update.message.reply_text("Transaction Does not exist.")
        return ConversationHandler.END
    res_amount = res.get('amount').get('value')
    try:
        current_balance = requests.get(f'{BACK_URL}/users/{user_id}/').json().get('user',{}).get('balance',0)
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
    
    # Check if user is registered
    response = requests.get(f'{BACK_URL}/accounts/filter-users/{user_id}/')
    if response.status_code != 200:
        await update.message.reply_text(
            "You need to register first before inviting others. Use the /register command."
        )
        return

    # Get user's wallet balance
    wallet_response = requests.get(f'{BACK_URL}/payments/wallet/{user_id}/').json()
    balance = wallet_response.get('balance', 0)

    invite_link = f"https://t.me/wowbingobot?start={user_id}"
    
    message = (
        f"🎮 Invite your friends to Wow Bingo!\n\n"
        f"Share this link with your friends:\n{invite_link}\n\n"
        f"Your current balance: {balance} ETB\n\n"
        f"Invite friends and enjoy playing together! 🎲"
    )

    # Add 20 ETB bonus for inviting
    requests.post(f'{BACK_URL}/payments/wallet/add-balance/', json={
        'user_id': user_id,
        'amount': 20
    })
    
    await update.message.reply_text(message)



def main() -> None:
    BOT_TOKEN = get_bot_seetings().get("bot_token")
    application = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()
    register_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('register', begin_register)],
        states={
            PHONE: [MessageHandler(filters.CONTACT, handle_phone)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    deposit_conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button)],
        states={
            # get_deposit_amount
            DEPOSIT_AMOUNT          : [MessageHandler(filters.TEXT & ~filters.COMMAND, deposit_amount)],
            GET_WITHDRAW_ACCOUNT    : [MessageHandler(filters.TEXT & ~filters.COMMAND, get_withdraw_account)],
            WITHDRAW_AMOUNT_CONFIRM : [MessageHandler(filters.TEXT & ~filters.COMMAND, get_withdraw_amount)],
            GET_TRANSCATION_DETAILS  : [MessageHandler(filters.TEXT & ~filters.COMMAND, get_transcation_details)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

  
 

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('play', play_command))
    application.add_handler(CommandHandler('instructions', instruction_command))
    application.add_handler(CommandHandler('support', support_command))
    application.add_handler(CommandHandler('withdraw', withdraw_command))
    application.add_handler(deposit_conversation_handler)
    application.add_handler(CommandHandler('invite', handle_invite))  
    application.add_handler(register_conversation_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

async def conversation_timeout(context):
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Conversation timed out due to inactivity. Please start again."
    )

async def cancel(update, context):
    await update.message.reply_text("Conversation cancelled. You can start again anytime.")
    return ConversationHandler.END