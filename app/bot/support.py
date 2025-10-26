from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import ConversationHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from telegram.ext import ApplicationBuilder, CommandHandler
import logging
import sys
import os

# Add Django setup
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django
django.setup()

from users.models import User
from wallet.models import Transaction, WithdrawalRequest
from asgiref.sync import sync_to_async

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Simple in-memory stores for demonstration ---
blocked_users = set()
logged_in_users = {}  # Store logged-in user sessions

ADMIN_ID = 1464395537  # Set your Telegram user ID as admin for sensitive actions
SUPPORT_IDS = [1464395537]  # List of Telegram user IDs for support staff

async def admin_check(update: Update):
    """Check if user is admin"""
    # Handle both regular updates and callback queries
    if hasattr(update, 'effective_user'):
        user_id = update.effective_user.id
    else:
        user_id = update.from_user.id
    return user_id == ADMIN_ID

async def support_check(update: Update):
    """Check if user is support staff or admin"""
    # Handle both regular updates and callback queries
    if hasattr(update, 'effective_user'):
        user_id = update.effective_user.id
    else:
        user_id = update.from_user.id
    
    # Check if user is admin or support staff
    is_admin = user_id == ADMIN_ID
    is_support = user_id in SUPPORT_IDS
    
    return is_admin or is_support

async def is_user_logged_in(telegram_id):
    """Check if user is logged in"""
    return telegram_id in logged_in_users

async def get_logged_in_user(telegram_id):
    """Get logged-in user data"""
    return logged_in_users.get(telegram_id)

async def login_user(telegram_id, user_data):
    """Login user"""
    logged_in_users[telegram_id] = user_data

async def logout_user(telegram_id):
    """Logout user"""
    if telegram_id in logged_in_users:
        del logged_in_users[telegram_id]

# Login/Logout functionality
async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle login command"""
    # Handle both regular updates and callback queries
    if hasattr(update, 'effective_user'):
        telegram_id = update.effective_user.id
    else:
        telegram_id = update.from_user.id
    
    logger.info(f"🔐 Login attempt for telegram_id: {telegram_id}")
    
    # Check if already logged in
    if await is_user_logged_in(telegram_id):
        msg = "✅ You are already logged in!"
        logger.info(f"✅ User {telegram_id} already logged in")
        keyboard = [[InlineKeyboardButton("🎛️ Open Menu", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if hasattr(update, 'message'):
            await update.message.reply_text(msg, reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        return
    
    # Get user from database
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        msg = (
            f"❌ User not found in our system.\n"
            f"Your Telegram ID: {telegram_id}\n"
            "Please contact support to register your account."
        )
        logger.warning(f"❌ Login failed - user not found for telegram_id: {telegram_id}")
        keyboard = [[InlineKeyboardButton("❓ Help", callback_data="help")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if hasattr(update, 'message'):
            await update.message.reply_text(msg, reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        return
    
    # Login user
    user_data = {
        'id': user.id,
        'username': user.username,
        'telegram_id': user.telegram_id,
        'phone': user.phone,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'login_time': update.message.date if hasattr(update, 'message') else update.callback_query.message.date
    }
    await login_user(telegram_id, user_data)
    logger.info(f"✅ User {user.username} logged in successfully")
    
    welcome_msg = (
        f"🎉 Welcome back, {user.first_name}!\n\n"
        f"📋 Account Details:\n"
        f"• Username: @{user.username}\n"
        f"• Phone: {user.phone}\n"
        f"• Telegram ID: {user.telegram_id}\n\n"
        f"✅ You are now logged in and can access all features!"
    )
    
    keyboard = [[InlineKeyboardButton("🎛️ Open Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'message'):
        await update.message.reply_text(welcome_msg, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(welcome_msg, reply_markup=reply_markup)

async def logout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle logout command"""
    # Handle both regular updates and callback queries
    if hasattr(update, 'effective_user'):
        telegram_id = update.effective_user.id
    else:
        telegram_id = update.from_user.id
    
    if not await is_user_logged_in(telegram_id):
        msg = "❌ You are not logged in!"
        keyboard = [[InlineKeyboardButton("🔐 Login", callback_data="login")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if hasattr(update, 'message'):
            await update.message.reply_text(msg, reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        return
    
    user_data = await get_logged_in_user(telegram_id)
    await logout_user(telegram_id)
    
    msg = (
        f"👋 Goodbye, {user_data['first_name']}!\n"
        f"You have been logged out successfully.\n\n"
        f"Use /login to log back in anytime."
    )
    
    keyboard = [[InlineKeyboardButton("🔐 Login", callback_data="login")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'message'):
        await update.message.reply_text(msg, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(msg, reply_markup=reply_markup)

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user profile"""
    # Handle both regular updates and callback queries
    if hasattr(update, 'effective_user'):
        telegram_id = update.effective_user.id
    else:
        telegram_id = update.from_user.id
    
    if not await is_user_logged_in(telegram_id):
        keyboard = [[InlineKeyboardButton("🔐 Login", callback_data="login")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = "❌ You need to login first to view your profile."
        
        if hasattr(update, 'message'):
            await update.message.reply_text(msg, reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        return
    
    user_data = await get_logged_in_user(telegram_id)
    
    profile_msg = (
        f"👤 Your Profile\n\n"
        f"• Name: {user_data['first_name']} {user_data.get('last_name', '')}\n"
        f"• Username: @{user_data['username']}\n"
        f"• Phone: {user_data['phone']}\n"
        f"• Telegram ID: {user_data['telegram_id']}\n"
        f"• Login Time: {user_data['login_time'].strftime('%Y-%m-%d %H:%M')}\n\n"
        f"✅ Status: Logged In"
    )
    
    keyboard = [
        [InlineKeyboardButton("📄 View Transactions", callback_data="transactions")],
        [InlineKeyboardButton("⏳ View Pending Requests", callback_data="pending_requests")],
        [InlineKeyboardButton("🚪 Logout", callback_data="logout")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'message'):
        await update.message.reply_text(profile_msg, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(profile_msg, reply_markup=reply_markup)

# Django ORM helper functions
@sync_to_async
def get_user_by_telegram_id(telegram_id):
    """Get user by telegram ID"""
    logger.info(f"🔍 Looking for user with telegram_id: {telegram_id}")
    try:
        user = User.objects.get(telegram_id=telegram_id)
        logger.info(f"✅ Found user: {user.username} (ID: {user.id})")
        return user
    except User.DoesNotExist:
        logger.warning(f"❌ User not found with telegram_id: {telegram_id}")
        return None

@sync_to_async
def get_pending_withdrawals():
    """Get all pending withdrawal requests from Django"""
    logger.info("🔍 Fetching all pending withdrawal requests...")
    withdrawals = list(WithdrawalRequest.objects.filter(
        status='pending'
    ).select_related('user'))
    logger.info(f"📊 Found {len(withdrawals)} pending withdrawal requests")
    for w in withdrawals:
        logger.info(f"   - {w.user.username}: {w.amount} Birr (ID: {w.id})")
    return withdrawals

@sync_to_async
def get_user_transactions(telegram_id):
    """Get user's transaction history from Django"""
    logger.info(f"🔍 Getting transactions for telegram_id: {telegram_id}")
    try:
        user = User.objects.get(telegram_id=telegram_id)
        transactions = list(Transaction.objects.filter(user=user).order_by('-created_at')[:10])
        logger.info(f"📊 Found {len(transactions)} transactions for {user.username}")
        return transactions
    except User.DoesNotExist:
        logger.warning(f"❌ User not found for transactions: {telegram_id}")
        return []

@sync_to_async
def get_user_pending_requests(telegram_id):
    """Get user's pending withdrawal requests from Django"""
    logger.info(f"🔍 Getting pending requests for telegram_id: {telegram_id}")
    try:
        user = User.objects.get(telegram_id=telegram_id)
        requests = list(WithdrawalRequest.objects.filter(
            user=user,
            status='pending'
        ).order_by('-created_at'))
        logger.info(f"📊 Found {len(requests)} pending requests for {user.username}")
        for req in requests:
            logger.info(f"   - {req.amount} Birr (ID: {req.id})")
        return requests
    except User.DoesNotExist:
        logger.warning(f"❌ User not found for pending requests: {telegram_id}")
        return []

@sync_to_async
def get_withdrawal_by_id(withdrawal_id):
    """Get withdrawal request by ID"""
    try:
        return WithdrawalRequest.objects.get(id=withdrawal_id)
    except WithdrawalRequest.DoesNotExist:
        return None

@sync_to_async
def update_withdrawal_status(withdrawal_id, status, processed_by_id):
    """Update withdrawal request status"""
    from django.utils import timezone
    try:
        withdrawal = WithdrawalRequest.objects.get(id=withdrawal_id)
        withdrawal.status = status
        withdrawal.processed_at = timezone.now()
        
        # Get the admin user who processed it
        try:
            admin_user = User.objects.get(telegram_id=processed_by_id)
            withdrawal.processed_by = admin_user
        except User.DoesNotExist:
            pass  # Keep processed_by as None if admin not found
        
        withdrawal.save()
        return True
    except WithdrawalRequest.DoesNotExist:
        return False

async def notify_user_withdrawal_status(telegram_id, withdrawal, status, bot):
    """Notify user about withdrawal status change"""
    try:
        # Extract withdrawal data in a sync context
        withdrawal_data = await sync_to_async(lambda: {
            'amount': withdrawal.amount,
            'id': withdrawal.id,
            'created_at': withdrawal.created_at.strftime('%Y-%m-%d %H:%M')
        })()
        
        status_messages = {
            'approved': f"✅ Your withdrawal request of {withdrawal_data['amount']} Birr has been approved!",
            'rejected': f"❌ Your withdrawal request of {withdrawal_data['amount']} Birr has been rejected.",
            'completed': f"🎉 Your withdrawal request of {withdrawal_data['amount']} Birr has been completed!"
        }
        
        message = status_messages.get(status, f"Your withdrawal request status has been updated to: {status}")
        
        # Send notification to user
        await bot.send_message(
            chat_id=telegram_id,
            text=f"📢 Withdrawal Update\n\n{message}\n\nRequest ID: #{withdrawal_data['id']}\nAmount: {withdrawal_data['amount']} Birr\nDate: {withdrawal_data['created_at']}"
        )
        
        logger.info(f"📤 Notification sent to user {telegram_id} for withdrawal #{withdrawal_data['id']}")
        
    except Exception as e:
        logger.error(f"Error sending notification to user {telegram_id}: {e}")

# View ALL pending requests with pagination and search
async def view_pending_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("🔍 view_pending_requests called - fetching ALL pending requests")
    
    # Get search query and page from context
    search_query = context.user_data.get('withdrawal_search', '').lower()
    current_page = context.user_data.get('withdrawal_page', 0)
    requests_per_page = 5
    
    # Get all pending requests
    all_requests = await get_pending_withdrawals()
    logger.info(f"📊 Retrieved {len(all_requests)} total pending requests")
    
    # Filter requests based on search query
    if search_query:
        # Remove @ symbol if present for username search
        clean_search = search_query.replace('@', '').lower()
        filtered_requests = [
            req for req in all_requests 
            if (clean_search in (req.user.username or '').lower() or 
                search_query in str(req.user.telegram_id) or
                search_query in str(req.amount) or
                clean_search in (req.user.first_name or '').lower())
        ]
        logger.info(f"🔍 Filtered to {len(filtered_requests)} requests matching '{search_query}'")
    else:
        filtered_requests = all_requests
    
    # Calculate pagination
    total_pages = (len(filtered_requests) + requests_per_page - 1) // requests_per_page
    if current_page >= total_pages:
        current_page = max(0, total_pages - 1)
    
    start_idx = current_page * requests_per_page
    end_idx = start_idx + requests_per_page
    page_requests = filtered_requests[start_idx:end_idx]
    
    if not page_requests:
        if search_query:
            msg = f"⏳ No pending withdrawal requests found matching '{search_query}'."
        else:
            msg = "⏳ No pending withdrawal requests found."
        logger.info("📝 No requests found for current page")
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if hasattr(update, 'message'):
            await update.message.reply_text(msg, reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
        return
    else:
        # Send header message first
        header_msg = f"⏳ All Pending Withdrawal Requests"
        if search_query:
            header_msg += f" (Search: '{search_query}')"
        header_msg += f"\n📄 Page {current_page + 1} of {total_pages}\n"
        
        logger.info(f"📝 Building messages for {len(page_requests)} requests on page {current_page + 1}")
        
        # Send header
        if hasattr(update, 'message'):
            await update.message.reply_text(header_msg)
        else:
            await update.callback_query.edit_message_text(header_msg)
        
        # Send each request with its own buttons
        for idx, request in enumerate(page_requests, start_idx + 1):
            # Extract request data in a sync context to avoid async/sync issues
            request_data = await sync_to_async(lambda req: {
                'username': req.user.username or "No username",
                'phone': req.user.phone or "No phone", 
                'telegram_id': req.user.telegram_id,
                'amount': req.amount,
                'created_at': req.created_at.strftime('%Y-%m-%d %H:%M'),
                'status': req.status,
                'admin_notes': req.admin_notes or 'No notes'
            })(request)
            
            request_msg = (
                f"{idx}. 👤 User Info:\n"
                f"   📱 Phone: {request_data['phone']}\n"
                f"   👤 Username: @{request_data['username']}\n"
                f"   🆔 Telegram ID: {request_data['telegram_id']}\n"
                f"   💰 Amount: {request_data['amount']} Birr\n"
                f"   📅 Date: {request_data['created_at']}\n"
                f"   📊 Status: {request_data['status']}\n"
                f"   📝 Notes: {request_data['admin_notes']}"
            )
            
            # Create keyboard for this specific request
            keyboard = []
            if request_data['status'] == 'pending':
                # Action buttons for pending requests
                action_buttons = [
                    InlineKeyboardButton(f"✅ Approve #{idx}", callback_data=f"approve_withdrawal_{request.id}"),
                    InlineKeyboardButton(f"❌ Reject #{idx}", callback_data=f"reject_withdrawal_{request.id}")
                ]
                keyboard.append(action_buttons)
            elif request.status == 'approved':
                # Action button for approved requests
                keyboard.append([InlineKeyboardButton(f"✅ Complete #{idx}", callback_data=f"complete_withdrawal_{request.id}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send this request with its buttons
            if hasattr(update, 'effective_chat'):
                chat_id = update.effective_chat.id
            else:
                chat_id = update.message.chat_id
            await context.bot.send_message(
                chat_id=chat_id,
                text=request_msg,
                reply_markup=reply_markup
            )
        
        # Send navigation and control buttons
        control_keyboard = []
        
        # Search button
        control_keyboard.append([InlineKeyboardButton("🔍 Search Requests", callback_data="search_withdrawals")])
        
        # Navigation buttons
        nav_buttons = []
        if current_page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"withdrawals_page_{current_page - 1}"))
        if current_page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"withdrawals_page_{current_page + 1}"))
        
        if nav_buttons:
            control_keyboard.append(nav_buttons)
        
        # Back to menu button
        control_keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")])
        
        control_reply_markup = InlineKeyboardMarkup(control_keyboard)
        
        # Send control buttons
        if hasattr(update, 'effective_chat'):
            chat_id = update.effective_chat.id
        else:
            chat_id = update.message.chat_id
        await context.bot.send_message(
            chat_id=chat_id,
            text="🎛️ Controls:",
            reply_markup=control_reply_markup
        )

# Handle withdrawal status changes
async def approve_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve a withdrawal request"""
    query = update.callback_query if hasattr(update, 'callback_query') else update
    await query.answer()
    
    if not await support_check(update):
        await query.edit_message_text("❌ Not authorized to approve withdrawals.")
        return
    
    withdrawal_id = int(query.data.split("_")[-1])
    logger.info(f"🔍 Approving withdrawal request ID: {withdrawal_id}")
    
    try:
        withdrawal = await get_withdrawal_by_id(withdrawal_id)
        if not withdrawal:
            await query.edit_message_text("❌ Withdrawal request not found.")
            return
        
        # Extract withdrawal status in a sync context
        withdrawal_status = await sync_to_async(lambda w: w.status)(withdrawal)
        
        if withdrawal_status != 'pending':
            await query.edit_message_text(f"❌ Withdrawal request is already {withdrawal_status}.")
            return
        
        # Update status to approved
        await update_withdrawal_status(withdrawal_id, 'approved', query.from_user.id)
        
        # Extract user telegram_id in a sync context
        user_telegram_id = await sync_to_async(lambda w: w.user.telegram_id)(withdrawal)
        
        # Notify user
        await notify_user_withdrawal_status(user_telegram_id, withdrawal, 'approved', context.bot)
        
        await query.edit_message_text(f"✅ Withdrawal request #{withdrawal_id} approved successfully!")
        
        # Refresh the withdrawal requests view
        await view_pending_requests(update, context)
        
    except Exception as e:
        logger.error(f"Error approving withdrawal: {e}")
        await query.edit_message_text("❌ Error approving withdrawal request.")

async def reject_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reject a withdrawal request"""
    query = update.callback_query if hasattr(update, 'callback_query') else update
    await query.answer()
    
    if not await support_check(update):
        await query.edit_message_text("❌ Not authorized to reject withdrawals.")
        return
    
    withdrawal_id = int(query.data.split("_")[-1])
    logger.info(f"🔍 Rejecting withdrawal request ID: {withdrawal_id}")
    
    try:
        withdrawal = await get_withdrawal_by_id(withdrawal_id)
        if not withdrawal:
            await query.edit_message_text("❌ Withdrawal request not found.")
            return
        
        # Extract withdrawal status in a sync context
        withdrawal_status = await sync_to_async(lambda w: w.status)(withdrawal)
        
        if withdrawal_status != 'pending':
            await query.edit_message_text(f"❌ Withdrawal request is already {withdrawal_status}.")
            return
        
        # Update status to rejected
        await update_withdrawal_status(withdrawal_id, 'rejected', query.from_user.id)
        
        # Extract user telegram_id in a sync context
        user_telegram_id = await sync_to_async(lambda w: w.user.telegram_id)(withdrawal)
        
        # Notify user
        await notify_user_withdrawal_status(user_telegram_id, withdrawal, 'rejected', context.bot)
        
        await query.edit_message_text(f"❌ Withdrawal request #{withdrawal_id} rejected.")
        
        # Refresh the withdrawal requests view
        await view_pending_requests(update, context)
        
    except Exception as e:
        logger.error(f"Error rejecting withdrawal: {e}")
        await query.edit_message_text("❌ Error rejecting withdrawal request.")

async def complete_withdrawal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Complete a withdrawal request"""
    query = update.callback_query if hasattr(update, 'callback_query') else update
    await query.answer()
    
    if not await support_check(update):
        await query.edit_message_text("❌ Not authorized to complete withdrawals.")
        return
    
    withdrawal_id = int(query.data.split("_")[-1])
    logger.info(f"🔍 Completing withdrawal request ID: {withdrawal_id}")
    
    try:
        withdrawal = await get_withdrawal_by_id(withdrawal_id)
        if not withdrawal:
            await query.edit_message_text("❌ Withdrawal request not found.")
            return
        
        # Extract withdrawal status in a sync context
        withdrawal_status = await sync_to_async(lambda w: w.status)(withdrawal)
        
        if withdrawal_status != 'approved':
            await query.edit_message_text(f"❌ Withdrawal request must be approved first. Current status: {withdrawal_status}")
            return
        
        # Update status to completed
        await update_withdrawal_status(withdrawal_id, 'completed', query.from_user.id)
        
        # Extract user telegram_id in a sync context
        user_telegram_id = await sync_to_async(lambda w: w.user.telegram_id)(withdrawal)
        
        # Notify user
        await notify_user_withdrawal_status(user_telegram_id, withdrawal, 'completed', context.bot)
        
        await query.edit_message_text(f"✅ Withdrawal request #{withdrawal_id} completed successfully!")
        
        # Refresh the withdrawal requests view
        await view_pending_requests(update, context)
        
    except Exception as e:
        logger.error(f"Error completing withdrawal: {e}")
        await query.edit_message_text("❌ Error completing withdrawal request.")

# Support staff management commands
async def add_support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add support staff (admin only)"""
    if not await admin_check(update):
        await update.message.reply_text("❌ Only admins can add support staff.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /add_support <telegram_user_id>")
        return
    
    try:
        support_id = int(context.args[0])
        if support_id not in SUPPORT_IDS:
            SUPPORT_IDS.append(support_id)
            await update.message.reply_text(f"✅ Added {support_id} to support staff.")
        else:
            await update.message.reply_text(f"❌ {support_id} is already a support staff member.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Please provide a valid Telegram user ID.")

async def remove_support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove support staff (admin only)"""
    if not await admin_check(update):
        await update.message.reply_text("❌ Only admins can remove support staff.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /remove_support <telegram_user_id>")
        return
    
    try:
        support_id = int(context.args[0])
        if support_id in SUPPORT_IDS:
            SUPPORT_IDS.remove(support_id)
            await update.message.reply_text(f"✅ Removed {support_id} from support staff.")
        else:
            await update.message.reply_text(f"❌ {support_id} is not a support staff member.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID. Please provide a valid Telegram user ID.")

async def list_support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List support staff (admin only)"""
    if not await admin_check(update):
        await update.message.reply_text("❌ Only admins can view support staff list.")
        return
    
    if not SUPPORT_IDS:
        await update.message.reply_text("📋 No support staff members added yet.")
        return
    
    support_list = "\n".join([f"• {support_id}" for support_id in SUPPORT_IDS])
    await update.message.reply_text(f"📋 Support Staff Members:\n{support_list}")

# Search withdrawal requests
async def search_withdrawals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search withdrawal requests"""
    logger.info("🔍 Search withdrawals called")
    
    msg = (
        "🔍 Search Withdrawal Requests\n\n"
        "Please send me a search term. I'll search by:\n"
        "• Username\n"
        "• Telegram ID\n"
        "• Amount\n"
        "• First name\n\n"
        "Send your search term now:"
    )
    
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="pending_requests")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(msg, reply_markup=reply_markup)
    
    # Set state to wait for search input
    context.user_data['waiting_for_search'] = True
    return "SEARCH_INPUT"

# Handle search input
async def handle_search_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle search input for withdrawal requests"""
    search_term = update.message.text.strip()
    logger.info(f"🔍 Search input received: '{search_term}'")
    
    # Store search query and reset page
    context.user_data['withdrawal_search'] = search_term
    context.user_data['withdrawal_page'] = 0
    context.user_data['waiting_for_search'] = False
    
    # Show results
    await view_pending_requests(update, context)
    return ConversationHandler.END

# Transaction history
async def view_transactions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Handle both regular updates and callback queries
    if hasattr(update, 'effective_user'):
        user_id = update.effective_user.id
    else:
        user_id = update.from_user.id
        
    history = await get_user_transactions(user_id)
    
    if not history:
        msg = "🕘 No transactions found."
    else:
        msg = "📄 Your Transaction History:\n\n"
        for idx, tx in enumerate(history, 1):
            msg += (
                f"{idx}. {tx.type.capitalize()} - {tx.amount} Birr\n"
                f"   Status: {tx.status}\n"
                f"   Date: {tx.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"   Reference: {tx.reference or 'N/A'}\n\n"
            )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'message'):
        await update.message.reply_text(msg, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(msg, reply_markup=reply_markup)

# Block user (admin only)
async def block_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_check(update):
        await update.message.reply_text("❌ Not authorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /block <user_id>")
        return
    try:
        user_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ Invalid user_id.")
        return
    blocked_users.add(user_id)
    await update.message.reply_text(f"✅ User {user_id} has been blocked.")

# Unblock user (admin only)
async def unblock_user_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await admin_check(update):
        await update.message.reply_text("❌ Not authorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /unblock <user_id>")
        return
    try:
        user_id = int(context.args[0])
    except:
        await update.message.reply_text("❌ Invalid user_id.")
        return
    if user_id in blocked_users:
        blocked_users.remove(user_id)
        await update.message.reply_text(f"✅ User {user_id} is unblocked.")
    else:
        await update.message.reply_text("User was not blocked.")

# Admin: View withdraw requests
async def view_withdraw_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("🔍 Admin view_withdraw_requests called")
    
    if not await admin_check(update):
        msg = "❌ Not authorized."
        logger.warning("❌ Admin check failed")
    else:
        logger.info("✅ Admin check passed, fetching withdrawals")
        withdrawals = await get_pending_withdrawals()
        logger.info(f"📊 Retrieved {len(withdrawals)} withdrawals for admin")
        
        if not withdrawals:
            msg = "📋 No pending withdrawal requests."
            logger.info("📝 No withdrawals found for admin")
        else:
            msg = "📋 **Pending Withdrawal Requests:**\n\n"
            logger.info(f"📝 Building admin message for {len(withdrawals)} withdrawals")
            for idx, withdrawal in enumerate(withdrawals, 1):
                msg += (f"{idx}. User: @{withdrawal.user.username or withdrawal.user.telegram_id}\n"
                        f"   Amount: {withdrawal.amount} Birr\n"
                        f"   Date: {withdrawal.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                        f"   Status: {withdrawal.status}\n"
                        f"   Notes: {withdrawal.admin_notes or 'No notes'}\n\n")
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    logger.info(f"📤 Sending admin message: {msg[:100]}...")
    
    if hasattr(update, 'message'):
        await update.message.reply_text(msg, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(msg, reply_markup=reply_markup, parse_mode='Markdown')

# Menu system
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command with welcome message and menu"""
    user = update.effective_user
    telegram_id = user.id
    
    # Check if user is logged in
    if await is_user_logged_in(telegram_id):
        user_data = await get_logged_in_user(telegram_id)
        welcome_text = (
            f"👋 Welcome back, {user_data['first_name']}!\n\n"
            "🎮 Empire Games Support Bot\n"
            "You are logged in and can access all features.\n\n"
            "Choose an option from the menu below:"
        )
        
        keyboard = [
            [InlineKeyboardButton("👤 My Profile", callback_data="profile")],
            [InlineKeyboardButton("📄 View Transactions", callback_data="transactions")],
            [InlineKeyboardButton("⏳ All Pending Requests", callback_data="pending_requests")],
            [InlineKeyboardButton("❓ Help & Support", callback_data="help")],
            [InlineKeyboardButton("ℹ️ About", callback_data="about")],
            [InlineKeyboardButton("🚪 Logout", callback_data="logout")]
        ]
    else:
        welcome_text = (
            f"👋 Welcome {user.first_name}!\n\n"
            "🎮 Welcome to Empire Games Support Bot!\n"
            "Please login to access all features.\n\n"
            "Choose an option from the menu below:"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔐 Login", callback_data="login")],
            [InlineKeyboardButton("❓ Help & Support", callback_data="help")],
            [InlineKeyboardButton("ℹ️ About", callback_data="about")]
        ]
    
    # Add admin menu if user is admin
    if await admin_check(update):
        keyboard.append([InlineKeyboardButton("🔧 Admin Panel", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu"""
    # Handle both regular updates and callback queries
    if hasattr(update, 'effective_user'):
        telegram_id = update.effective_user.id
    else:
        telegram_id = update.from_user.id
    
    # Check if user is logged in
    if await is_user_logged_in(telegram_id):
        keyboard = [
            [InlineKeyboardButton("👤 My Profile", callback_data="profile")],
            [InlineKeyboardButton("📄 View Transactions", callback_data="transactions")],
            [InlineKeyboardButton("⏳ All Pending Requests", callback_data="pending_requests")],
            [InlineKeyboardButton("❓ Help & Support", callback_data="help")],
            [InlineKeyboardButton("ℹ️ About", callback_data="about")],
            [InlineKeyboardButton("🚪 Logout", callback_data="logout")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🔐 Login", callback_data="login")],
            [InlineKeyboardButton("❓ Help & Support", callback_data="help")],
            [InlineKeyboardButton("ℹ️ About", callback_data="about")]
        ]
    
    # Add admin menu if user is admin
    if await admin_check(update):
        keyboard.append([InlineKeyboardButton("🔧 Admin Panel", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'message'):
        await update.message.reply_text("🎛️ Main Menu:", reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text("🎛️ Main Menu:", reply_markup=reply_markup)

async def handle_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu callback queries"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "login":
        await login_command(query, context)
    elif query.data == "logout":
        await logout_command(query, context)
    elif query.data == "profile":
        await profile_command(query, context)
    elif query.data == "transactions":
        await view_transactions(query, context)
    elif query.data == "pending_requests":
        await view_pending_requests(query, context)
    elif query.data == "help":
        await show_help(query, context)
    elif query.data == "about":
        await show_about(query, context)
    elif query.data == "admin_panel":
        await show_admin_panel(query, context)
    elif query.data == "main_menu":
        await main_menu(query, context)
    elif query.data == "view_withdraw_requests":
        await view_withdraw_requests(query, context)
    elif query.data == "view_blocked_users":
        await view_blocked_users(query, context)
    elif query.data == "system_stats":
        await system_stats(query, context)
    elif query.data == "search_withdrawals":
        await search_withdrawals(query, context)
    elif query.data.startswith("withdrawals_page_"):
        # Handle pagination
        page_num = int(query.data.split("_")[-1])
        context.user_data['withdrawal_page'] = page_num
        await view_pending_requests(query, context)
    elif query.data.startswith("approve_withdrawal_"):
        await approve_withdrawal(query, context)
    elif query.data.startswith("reject_withdrawal_"):
        await reject_withdrawal(query, context)
    elif query.data.startswith("complete_withdrawal_"):
        await complete_withdrawal(query, context)

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information"""
    help_text = (
        "❓ **Help & Support**\n\n"
        "**Available Commands:**\n"
        "• `/start` - Show main menu\n"
        "• `/menu` - Open main menu\n"
        "• `/login` - Login to your account\n"
        "• `/logout` - Logout from your account\n"
        "• `/profile` - View your profile\n"
        "• `/transactions` - View transaction history\n\n"
        "**Menu Options:**\n"
        "• 🔐 Login - Access your account\n"
        "• 👤 My Profile - View account details\n"
        "• 📄 View Transactions - See your transaction history\n"
        "• ⏳ All Pending Requests - View all pending withdrawal requests\n"
        "• ❓ Help & Support - Get help information\n"
        "• ℹ️ About - Learn about the bot\n"
        "• 🚪 Logout - Sign out of your account\n\n"
        "**How to use:**\n"
        "1. Use `/login` to access your account\n"
        "2. Use the menu buttons for easy navigation\n"
        "3. Check your transaction history and pending requests\n"
        "4. Contact support for assistance\n\n"
        "**Need more help?**\n"
        "Contact our support team for assistance!"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'message'):
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show about information"""
    about_text = (
        "ℹ️ **About Empire Games Support Bot**\n\n"
        "**Version:** 1.0.0\n"
        "**Purpose:** Support bot for Empire Games platform\n\n"
        "**Features:**\n"
        "• Transaction history viewing\n"
        "• Admin management tools\n"
        "• User support\n"
        "• Withdrawal request monitoring\n\n"
        "**Contact:**\n"
        "For support, use the help menu or contact our team."
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(update, 'message'):
        await update.message.reply_text(about_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(about_text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel"""
    if not await admin_check(update):
        await update.callback_query.edit_message_text("❌ Not authorized.")
        return
    
    admin_text = "🔧 **Admin Panel**\n\nChoose an admin action:"
    
    keyboard = [
        [InlineKeyboardButton("📋 View Withdraw Requests", callback_data="view_withdraw_requests")],
        [InlineKeyboardButton("🚫 View Blocked Users", callback_data="view_blocked_users")],
        [InlineKeyboardButton("📊 System Stats", callback_data="system_stats")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(admin_text, reply_markup=reply_markup, parse_mode='Markdown')

async def view_blocked_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View blocked users (admin only)"""
    if not await admin_check(update):
        await update.callback_query.edit_message_text("❌ Not authorized.")
        return
    
    if not blocked_users:
        msg = "No users are currently blocked."
    else:
        msg = "🚫 **Blocked Users:**\n\n"
        for user_id in blocked_users:
            msg += f"• User ID: {user_id}\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(msg, reply_markup=reply_markup, parse_mode='Markdown')

async def system_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show system statistics (admin only)"""
    if not await admin_check(update):
        await update.callback_query.edit_message_text("❌ Not authorized.")
        return
    
    # Get Django data
    pending_withdrawals = await get_pending_withdrawals()
    total_transactions = await sync_to_async(lambda: Transaction.objects.count())()
    
    stats_text = (
        "📊 **System Statistics**\n\n"
        f"• Pending Withdrawal Requests: {len(pending_withdrawals)}\n"
        f"• Total Transactions: {total_transactions}\n"
        f"• Blocked Users: {len(blocked_users)}\n"
        f"• Total Users: {await sync_to_async(lambda: User.objects.count())()}\n"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')

# Helper to plug into main bot setup_handlers:
support_handlers = {
    "view_transactions": view_transactions,
    "block_user_command": block_user_command,
    "unblock_user_command": unblock_user_command,
    "view_withdraw_requests": view_withdraw_requests,
}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting support bot...")
    try:
        app = ApplicationBuilder().token("8154094611:AAFF2uibjzso6VHqGkgEtf17l1L7MnOZ1nY").build()
        
        # Add command handlers
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("menu", main_menu))
        app.add_handler(CommandHandler("login", login_command))
        app.add_handler(CommandHandler("logout", logout_command))
        app.add_handler(CommandHandler("profile", profile_command))
        app.add_handler(CommandHandler("transactions", view_transactions))
        app.add_handler(CommandHandler("block", block_user_command))
        app.add_handler(CommandHandler("unblock", unblock_user_command))
        app.add_handler(CommandHandler("withdraw_requests", view_withdraw_requests))
        app.add_handler(CommandHandler("add_support", add_support_command))
        app.add_handler(CommandHandler("remove_support", remove_support_command))
        app.add_handler(CommandHandler("list_support", list_support_command))
        
        # Add conversation handler for search
        search_conversation = ConversationHandler(
            entry_points=[CallbackQueryHandler(search_withdrawals, pattern="^search_withdrawals$")],
            states={
                "SEARCH_INPUT": [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_input)],
            },
            fallbacks=[CallbackQueryHandler(lambda u, c: view_pending_requests(u, c), pattern="^pending_requests$")]
        )
        app.add_handler(search_conversation)
        
        # Add callback query handler for menu and pagination
        app.add_handler(CallbackQueryHandler(
            handle_menu_callback,
            pattern="^(login|logout|profile|transactions|pending_requests|help|about|admin_panel|main_menu|view_withdraw_requests|view_blocked_users|system_stats|search_withdrawals|withdrawals_page_.*|approve_withdrawal_.*|reject_withdrawal_.*|complete_withdrawal_.*)$"
        ))
        
        # Set bot commands
        commands = [
            BotCommand("start", "Start the bot and show menu"),
            BotCommand("menu", "Open main menu"),
            BotCommand("login", "Login to your account"),
            BotCommand("logout", "Logout from your account"),
            BotCommand("profile", "View your profile"),
            BotCommand("transactions", "View transaction history"),
            BotCommand("help", "Show help information"),
            BotCommand("add_support", "Add support staff (admin only)"),
            BotCommand("remove_support", "Remove support staff (admin only)"),
            BotCommand("list_support", "List support staff (admin only)"),
        ]
        
        async def post_init(application):
            await application.bot.set_my_commands(commands)
            
        app.post_init = post_init
        
        app.run_polling()
   
    except Exception as e:
        logger.error(f"Error starting support bot: {e}")
        sys.exit(1)

