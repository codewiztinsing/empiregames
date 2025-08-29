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
from utils import get_bot_seetings   
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
from utils.handle_phone import handle_phone
from helpers import get_user_balance,get_payment_receivers,initialize_payment_manual,initialize_payment_request

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
DEPOSIT_AMOUNT = 1
GET_WITHDRAW_ACCOUNT = 2
WITHDRAW_AMOUNT_CONFIRM = 3
GET_TRANSCATION_DETAILS = 4
PHONE_NUMBER = 5
PHONE = 6  # Add PHONE state for registration


CONVERSATION_TIMEOUT = 300  # 5 minutes




    
    


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("🎮 Play", callback_data='play'),
         InlineKeyboardButton("📝 Register",callback_data = "register")],
        [InlineKeyboardButton("💰 Check Balance", callback_data='check_balance'),
         InlineKeyboardButton("💳 Deposit", callback_data='deposit')],
        [InlineKeyboardButton("📞 Contact Support", callback_data='contact_support'),
         InlineKeyboardButton("🔗 Join Group", url='https://t.me/AkerBingoGroup')]
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
    await update.message.reply_text('Welcome to Aker Bingo! Select an option:', reply_markup=reply_markup)
    
    # Only set up job queue if it exists
    if hasattr(context, 'job_queue') and context.job_queue:
        context.job_queue.run_once(conversation_timeout, CONVERSATION_TIMEOUT, chat_id=update.effective_chat.id)
    
    # Start command doesn't need to return a conversation state
    return


# Function to create the play options keyboardF
def play_options_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🎮 Play 10", callback_data='10')
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


def get_available_banks():
    """Get available banks for withdrawal"""
    # This is a placeholder - you should implement this to get banks from your API
    return {
        "data": [
            {"id": "1", "name": "Telebirr"},
            {"id": "2", "name": "CBE Bank"}
        ]
    }

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
        logger.info(f"wallet url {BACK_URL}/api/v1/users/{telegram_id}")

        user = requests.get(f'{BACK_URL}/api/v1/users/{telegram_id}').json()
        logger.info(f"user {user.get("balance")}")
        balance = float(user.get('balance', 0))
        logger.info(f"balance {balance}")
      
        if int(balance) < 20:
            await update.message.reply_text(f"You must leave at least 20 ETB in your wallet. Please enter a smaller amount.")
            return WITHDRAW_AMOUNT_CONFIRM

      

        if int(amount) > 150:
            await update.message.reply_text(f"Withdrawal amount must be less than 150 ETB")
            return WITHDRAW_AMOUNT_CONFIRM


        if int(amount) < 100:
            await update.message.reply_text(f"Withdrawal amount must be at least 100 ETB")
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
                f"Please enter your phone or account number  where you want to receive the withdrawal:"
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
        logger.info(f"account_number {account_number}")
        context.user_data['withdraw_account'] = account_number
        logger.info(f"context.user_data['withdraw_account'] {context.user_data['withdraw_account']}")
        
        # Get withdrawal details from context
        amount = context.user_data.get('withdraw_amount')
        telegram_id = update.effective_user.id
        
        # Initialize payment request with amount and telegram_id
        response = initialize_payment_request(amount, telegram_id)
        logger.info(f"response {response}")
        # Notify user to wait patiently for message from bank
        await update.message.reply_text(
            "✅ Your withdrawal request has been submitted successfully!\n\n"
            "📱 Please wait patiently for a message from your bank regarding the withdrawal.\n"
            "⏰ This process may take a few minutes to complete.\n\n"
            "Thank you for your patience! 🙏"
        )
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
      
         [InlineKeyboardButton("🔙 Back to Menu", callback_data='back')]
    ]
    

    return InlineKeyboardMarkup(keyboard)


# Function to create the play options keyboard
def support_options_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📞 Support 1 👨‍💼 -->  0912729725 📱",  url='https://t.me/WassihunT')],
       
    ]
    return InlineKeyboardMarkup(keyboard)

async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = support_options_keyboard()
    await update.message.reply_text("Contact us using support button. We will respond to your message as soon as possible.", reply_markup=reply_markup)

async def deposit_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Go to the next state for deposit amount input
    logger.info(f"context {context}")
    user_id = update.effective_user.id
    username = update.effective_user.username
    BACK_URL = get_bot_seetings().get("bot_url")
    # Check if user is registered
    response = requests.get(f'{BACK_URL}/api/v1/users/{user_id}')
    if response.status_code != 200:
        await update.message.reply_text(
            "You need to register first before making a deposit. Use the /register command."
        )
        return
    else:
        await update.message.reply_text("Please enter the amount you want to deposit (minimum 20 ETB):")
        # Set the conversation state to wait for amount input
        context.user_data['waiting_for_deposit'] = True
        return DEPOSIT_AMOUNT
        

async def check_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    balance = get_user_balance(user_id)
    username  = update.effective_user.username
    telegram_id = update.effective_user.id

    payment_summary = (
                    "🏦  Aker Bingo STATEMENT\n" +
                    f"💰  {balance} Birr\n" +
                    f"👥  {username} \n" +
                    f"📄 USER TELEGRAM ID: {telegram_id}\n" +
                    f"🔙 Back to Menu\n" 
                ) 
    await update.message.reply_text(text=payment_summary)
    
    return ConversationHandler.END



    
  

async def instruction_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = instructions_options_keyboard()  # Create the inline keyboard
    await update.message.reply_text("Choose a instruction option:", reply_markup=reply_markup)




async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    BACK_URL = get_bot_seetings().get("bot_url")
    GAME_URL = get_bot_seetings().get("GAME_URL")
    username = query.from_user.username 
    await query.answer()
  

    try:
        if query.data in ['10']:
            player_id = query.from_user.id
            logger.info(f"player_id = {player_id}")
            user_balance = get_user_balance(player_id)
            logger.info(f"user_balance = {user_balance}")
            if user_balance == 0:
                await query.edit_message_text(
                    text=f"You have no balance. Please deposit to play.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("Deposit", callback_data='deposit')
                    ]])
                )
                return ConversationHandler.END
            if user_balance < 10:
                await query.edit_message_text(
                    text=f"You have no balance. Please deposit to play.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("Deposit", callback_data='deposit')
                    ]])
                )
                return ConversationHandler.END

            web_app_url = f"{GAME_URL}?playerId={player_id}&betAmount={10}&playerName={query.from_user.username}&wallet_amount={user_balance}"
            logger.info(f"web_app_url = {web_app_url}")
            
            await query.edit_message_text(
                text=f"Starting game with 10 ETB bet...",
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
            return ConversationHandler.END

        elif query.data == 'contact_support':
            await query.edit_message_text(
                text="Choose a contact support:",
                reply_markup=support_options_keyboard()
            )
            return ConversationHandler.END


        elif query.data == 'get_deposit_amount':
          
            return DEPOSIT_AMOUNT

        elif query.data == 'confirm_deposit':
            # Get deposit details from context
            deposit_amount = context.user_data.get('deposit_amount')
            user_id = update.effective_user.id
            username = update.effective_user.username
            payment_receivers = get_payment_receivers(user_id)
            logger.info(f"payment_receivers {payment_receivers}")
            if payment_receivers:
                for receiver in payment_receivers:
                    logger.info(f"receiver {receiver}")
                    phone_number = receiver.get('phoneNumber')
                    account_number = receiver.get('accountNumber')
                # Construct payment instruction message
                payment_message = (
                    f"💳 **DEPOSIT INSTRUCTIONS**\n\n"
                    f"💰 Amount to deposit: **{deposit_amount} ETB**\n\n"
                    f"📱 **Transfer to any of these numbers:**\n"
                )
                
                for i, receiver in enumerate(payment_receivers, 1):
                    phone_number = receiver.get('phoneNumber')
                    account_number = receiver.get('accountNumber')
                    bank_name = receiver.get('bankName', 'Mobile Money')
                    
                    payment_message += f"{i}. {bank_name}\n"
                    if phone_number:
                        payment_message += f"   📞 Phone: {phone_number}\n"
                    if account_number:
                        payment_message += f"   🏦 Account: {account_number}\n"
                    payment_message += "\n"
                
                payment_message += (
                    f"📋 **IMPORTANT:**\n"
                    f"• Transfer exactly **{deposit_amount} ETB**\n"
                    f"• After transfer, send us the SMS/confirmation message you received from your bank\n"
                    f"• Include your transaction reference number\n"
                    f"• Your deposit will be processed within 5-10 minutes\n\n"
                    f"💬 Send your confirmation message now:"
                )
                
                await query.edit_message_text(
                    text=payment_message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("❌ Cancel", callback_data='cancel_deposit')
                    ]])
                )

                initialize_payment_manual(deposit_amount,phone_number,user_id)
                  
               
                return ConversationHandler.END
            else:
                await query.edit_message_text(
                    text=f"No payment receivers found. Please add a payment receiver first.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Add Payment Receiver", callback_data='add_payment_receiver')]])
                )
         
            
            return ConversationHandler.END

        elif query.data == 'cancel_deposit':
            await query.answer("Deposit cancelled.")
            await query.edit_message_text("❌ Deposit cancelled. You can start a new deposit anytime.")
            return ConversationHandler.END

         
        elif query.data == 'check_balance':
            BACK_URL = get_bot_seetings().get("server_url") 
            telegram_id = query.from_user.id
            balance = get_user_balance(telegram_id)
            username = query.from_user.username
          

            # Create payment summary with user details
            payment_summary = (
                    "🏦  Aker Bingo STATEMENT\n" +
                    f"💰  {balance} Birr\n" +
                    f"👥  {username} \n" +
                    f"📄 USER TELEGRAM ID: {telegram_id}\n" +
                    f"🔙 Back to Menu\n" 
                ) 
            await query.edit_message_text(text=payment_summary)
            return ConversationHandler.END

        
                
        

        elif query.data in ['10','20', '50','100']:

            player_id = query.from_user.id
            user_id = query.from_user.id
            username = query.from_user.username or query.from_user.first_name
            bet_amount = query.data
            user_balance = get_user_balance(user_id)
        
            web_app_url = (
                f"https://akerbingo.com/?playerId={player_id}&name={username}&betAmount={bet_amount}&wallet_amount={user_balance}"
            )

            keyboard = [
                [InlineKeyboardButton("Open Aker Bingo!", web_app=WebAppInfo(url=web_app_url))]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.message.reply_text("Start playing Aker Bingo", reply_markup=reply_markup)

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

        

        elif query.data == 'withraw_with_chapa':
            await query.edit_message_text(
                text="how much do you want to withdraw?"
            )
            return WITHDRAW_AMOUNT_CONFIRM

          
            
            
        
        elif query.data == 'cancel':
            await query.edit_message_text(text="Withdrawal request cancelled.")
            return ConversationHandler.END


        
        elif query.data == "register":
            # For registration, we need to start a conversation
            # Since this is a callback query, we'll send a new message with the keyboard
            await query.message.reply_text(
                text="Please share your phone number to complete registration.",
                reply_markup=ReplyKeyboardMarkup(
                    [[KeyboardButton("Share Contact", request_contact=True)]],
                    one_time_keyboard=True,
                    resize_keyboard=True
                )
            )
            return PHONE_NUMBER
           
        

          
          
          
        elif query.data == 'menu':
            keyboard = [
                [InlineKeyboardButton("Play Game", callback_data='play'),
                 InlineKeyboardButton("Check Balance", callback_data='check_balance')],
                [InlineKeyboardButton("Deposit", callback_data='deposit'),
                 InlineKeyboardButton("Register", callback_data='register')]

              
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Welcome to Aker Bingo! Please select an option:", reply_markup=reply_markup)
            return ConversationHandler.END
            
 
        else:

            keyboard = [
                [InlineKeyboardButton("Play Game", callback_data='play'),
                 InlineKeyboardButton("Check Balance", callback_data='check_balance')],
                [InlineKeyboardButton("Deposit", callback_data='deposit'),
                 InlineKeyboardButton("Register", callback_data='register')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Welcome to Aker Bingo! Please select an option:", reply_markup=reply_markup)
            return ConversationHandler.END
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

    response = requests.get(full_url).json()
    logger.info(f"response = {response}")
    phone = response.get("phoneNumber")
    logger.info(f"phone = {phone}")
    context.user_data['deposit_amount'] = amount    

    message = """
    <b>💳 Payment Receipt</b>
    <b>👤 Name:</b> {}  
    <b>📞 Phone:</b> {}  
    <b>💰 Amount:</b> {} ETB  
    <b>📅 Date:</b> {}
    """.format(update.effective_user.username,phone,amount,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    confirm_button = InlineKeyboardButton("Confirm", callback_data='confirm_deposit')
    cancel_button = InlineKeyboardButton("Cancel", callback_data='cancel_deposit')
    keyboard = [[confirm_button, cancel_button]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message,parse_mode=ParseMode.HTML,reply_markup=reply_markup)
    return ConversationHandler.END

    
  



async def get_transcation_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    BACK_URL = get_bot_seetings().get("bot_url")   
  
    message = update.message.text
    # Parse the message to extract transaction details
    try:
        # Assuming the message contains transaction details in some format
        # You may need to adjust this based on your actual message format
        user_id = update.effective_user.id
        username = update.effective_user.username
        
        # For now, let's assume the message contains the transaction number
        # You may need to implement proper parsing logic here
        transaction_number = message.strip()  # Simple parsing for now
        
        response = requests.get(f'{BACK_URL}/transactions/transactionId/{transaction_number}')
        res = response.json()
        if res.get('status') == 'error':
            await update.message.reply_text("Transaction Does not exist.")
            return ConversationHandler.END
        res_amount = res.get('amount').get('value')
        
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
        "register", 
        "Register"
    ),

    BotCommand(
        "play", 
        "Play"
    ),

    BotCommand(
        "deposit", 
        "Deposit"
        ),

  
      BotCommand(
        "balance", 
        "Balance"
        ),

    BotCommand(
        "withdraw", 
        "Withdraw"
        ),
    BotCommand(
        "invite", 
        "Invite"
        ),
    BotCommand(
        "support", 
        "Support"
        ),
    BotCommand(
            "contact", 
            "Contact"
            ),
    BotCommand(
        "sale", 
        "Sale"
        )

    ]


async def post_init(app):
    await app.bot.set_my_commands(all_public_commands_descriptions)


      
  

async def handle_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    BACK_URL = get_bot_seetings().get("bot_url")
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

    invite_link = f"https://t.me/akerbingobot?start={user_id}"
    
    message = (
        f"🎮 Invite your friends to Aker Bingo!\n\n"
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


async def conversation_timeout(context):
    await context.bot.send_message(
        chat_id=context.job.chat_id,
        text="Conversation timed out due to inactivity. Please start again."
    )

async def cancel(update, context):
    await update.message.reply_text("Conversation cancelled. You can start again anytime.")
    return ConversationHandler.END


def main() -> None:
    BOT_TOKEN = get_bot_seetings().get("bot_token")
    application = ApplicationBuilder().token("8408827169:AAEvrQiXPmbSQ3uxbhWuXzMYZCOmRLoeEVc").post_init(post_init).build()
    # Create a proper registration conversation handler
    register_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('register', handle_phone)],
        states={
            PHONE : [MessageHandler(filters.CONTACT, handle_phone)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # Main conversation handler for button interactions and other states
    deposit_conversation_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button), CommandHandler('deposit', deposit_command)],
        states={
            # get_deposit_amount
            DEPOSIT_AMOUNT          : [MessageHandler(filters.TEXT & ~filters.COMMAND, deposit_amount)],
            GET_WITHDRAW_ACCOUNT    : [MessageHandler(filters.TEXT & ~filters.COMMAND, get_withdraw_account)],
            WITHDRAW_AMOUNT_CONFIRM : [MessageHandler(filters.TEXT & ~filters.COMMAND, get_withdraw_amount)],
            GET_TRANSCATION_DETAILS  : [MessageHandler(filters.TEXT & ~filters.COMMAND, get_transcation_details)],
            PHONE_NUMBER            : [MessageHandler(filters.CONTACT, handle_phone)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

  
 

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('play', play_command))
    application.add_handler(CommandHandler('support', support_command))
    application.add_handler(CommandHandler('balance', check_balance_command))
    application.add_handler(CommandHandler('instructions', instruction_command))
    application.add_handler(CommandHandler('withdraw', withdraw_command))
    application.add_handler(deposit_conversation_handler)
    application.add_handler(CommandHandler('invite', handle_invite))  
    application.add_handler(register_conversation_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()