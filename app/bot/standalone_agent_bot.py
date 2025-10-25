#!/usr/bin/env python3
"""
Standalone Agent Bot
A Telegram bot for managing agents and their referrals independently from the main bot.
"""

import os
import sys
import logging
import uuid
import json
from datetime import datetime
from typing import Dict, Set, List, Optional
from pathlib import Path

# Add the parent directory to the path to import Django modules if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
import django
django.setup()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
)

# Import Django models
from users.models import User, Agent
from wallet.models import Transaction
from asgiref.sync import sync_to_async

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
REGISTER_AGENT, ADD_PLAYER, MANAGE_PLAYERS = range(3)

class AgentBot:
    def __init__(self, token: str):
        self.token = token
        self.application = ApplicationBuilder().token(token).build()
        self.setup_handlers()
        
    def generate_invite_code(self) -> str:
        """Creates a unique invite code"""
        return str(uuid.uuid4())[:8]
    
    @sync_to_async
    def get_or_create_user(self, telegram_id: int, username: str = None) -> User:
        """Get or create a user by telegram ID"""
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                'username': username or f"user_{telegram_id}",
                'is_active': True
            }
        )
        return user
    
    @sync_to_async
    def get_agent_by_user(self, user: User) -> Optional[Agent]:
        """Get agent by user"""
        try:
            return Agent.objects.get(user=user)
        except Agent.DoesNotExist:
            return None
    
    @sync_to_async
    def create_agent(self, user: User, invite_code: str) -> Agent:
        """Create a new agent"""
        return Agent.objects.create(
            user=user,
            referral_code=invite_code
        )
    
    @sync_to_async
    def get_agent_by_invite_code(self, invite_code: str) -> Optional[Agent]:
        """Get agent by invite code"""
        try:
            return Agent.objects.get(referral_code=invite_code)
        except Agent.DoesNotExist:
            return None
    
    @sync_to_async
    def get_agent_players(self, agent: Agent) -> List[User]:
        """Get all players referred by an agent"""
        return list(User.objects.filter(referred_by=agent.user))
    
    @sync_to_async
    def get_user_deposits(self, user: User) -> List[Transaction]:
        """Get all deposit transactions for a user"""
        return list(Transaction.objects.filter(
            user=user,
            type='DEPOSIT',
            status='success'
        ))
    
    @sync_to_async
    def update_user_referral(self, user: User, referrer: User) -> None:
        """Update user's referral information"""
        user.referred_by = referrer
        user.save()
    
    @sync_to_async
    def update_agent_commission(self, agent: Agent, amount: float) -> None:
        """Update agent's commission (placeholder - commission tracking not implemented in model)"""
        # TODO: Implement commission tracking in Agent model or separate Commission model
        pass
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        # Check if user came via referral link
        if context.args and len(context.args) > 0 and context.args[0].startswith("ref_"):
            await self.player_join(update, context)
            return
            
        welcome_message = f"""
🤖 Welcome to Agent Bot!

Hi {username}! This bot helps you manage agents and referrals.

Available commands:
/register_agent - Register as an agent
/agent_menu - Open agent menu
/my_stats - View your statistics
/help - Show this help message

If you have an invite link, use it to join as a player!
        """
        
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 Agent Bot Commands:

👤 For Players:
/start - Start the bot
/my_stats - View your statistics

👥 For Agents:
/register_agent - Register as an agent
/agent_menu - Open agent menu

📊 General:
/help - Show this help message

🔗 Referral System:
Agents can invite players using referral links.
Players who join via referral links are tracked.
Agents earn commission when their players deposit ≥100 Birr.
        """
        await update.message.reply_text(help_text)
    
    async def agent_register(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Register a new agent"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        # Get or create user
        user = await self.get_or_create_user(user_id, username)
        
        # Check if already an agent
        existing_agent = await self.get_agent_by_user(user)
        if existing_agent:
            await update.message.reply_text(
                f"✅ You're already registered as an agent!\n"
                f"Your invite link:\n"
                f"https://t.me/{context.bot.username}?start=ref_{existing_agent.referral_code}"
            )
            return ConversationHandler.END

        # Register new agent
        invite_code = self.generate_invite_code()
        agent = await self.create_agent(user, invite_code)
        
        await update.message.reply_text(
            f"🎉 Congratulations! You are now registered as an agent!\n\n"
            f"📋 Your Agent Details:\n"
            f"• Agent ID: {invite_code}\n"
            f"• Username: @{username}\n"
            f"• Registered: {agent.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"🔗 Share this link to invite players:\n"
            f"https://t.me/{context.bot.username}?start=ref_{invite_code}\n\n"
            f"💡 Use /agent_menu to manage your players!"
        )
        return ConversationHandler.END

    async def player_join(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle player joining via referral link"""
        if not (context.args and len(context.args) > 0 and context.args[0].startswith("ref_")):
            return
            
        invite_code = context.args[0][4:]
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        # Get or create user
        user = await self.get_or_create_user(user_id, username)
        
        # Check if agent exists
        agent = await self.get_agent_by_invite_code(invite_code)
        if not agent:
            await update.message.reply_text(
                "❌ Invalid referral link. Please contact the agent for a valid link."
            )
            return
            
        # Check if already referred by someone
        if user.referred_by:
            await update.message.reply_text(
                "✅ You're already registered as a player!"
            )
            return
            
        # Register new player referral
        await self.update_user_referral(user, agent.user)
        
        agent_username = agent.user.username or "Unknown"
        await update.message.reply_text(
            f"🎉 Welcome! You've successfully joined as a player!\n\n"
            f"📋 Your Details:\n"
            f"• Player ID: {user_id}\n"
            f"• Username: @{username}\n"
            f"• Invited by: @{agent_username}\n"
            f"• Joined: {user.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"💡 Use /my_stats to view your statistics!"
        )

    async def agent_view_players(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View agent's players with search and pagination"""
        # Handle both regular updates and callback queries
        if hasattr(update, 'effective_user'):
            user_id = update.effective_user.id
        else:
            user_id = update.from_user.id
            
        # Get user and agent
        user = await self.get_or_create_user(user_id)
        agent = await self.get_agent_by_user(user)
        
        if not agent:
            reply_text = "❌ You are not registered as an agent. Use /register_agent to register."
            if hasattr(update, 'message'):
                await update.message.reply_text(reply_text)
            else:
                await update.edit_message_text(reply_text)
            return ConversationHandler.END

        # Get all players
        all_players = await self.get_agent_players(agent)
        if not all_players:
            reply_text = (
                "📭 You have no players yet.\n\n"
                f"🔗 Share your invite link to get players:\n"
                f"https://t.me/{context.bot.username}?start=ref_{agent.referral_code}"
            )
            if hasattr(update, 'message'):
                await update.message.reply_text(reply_text)
            else:
                await update.edit_message_text(reply_text)
            return ConversationHandler.END

        # Get search query and page from context
        search_query = context.user_data.get('player_search', '').lower()
        current_page = context.user_data.get('player_page', 0)
        players_per_page = 5

        # Filter players based on search query
        if search_query:
            filtered_players = [
                p for p in all_players 
                if (search_query in p.username.lower() or 
                    search_query in str(p.telegram_id) or
                    search_query in p.first_name.lower() if p.first_name else False)
            ]
        else:
            filtered_players = all_players

        # Calculate pagination
        total_pages = (len(filtered_players) + players_per_page - 1) // players_per_page
        if current_page >= total_pages:
            current_page = max(0, total_pages - 1)
        
        start_idx = current_page * players_per_page
        end_idx = start_idx + players_per_page
        page_players = filtered_players[start_idx:end_idx]

        # Build message
        msg = f"👥 Your Players ({len(filtered_players)} of {len(all_players)} total)"
        if search_query:
            msg += f" - Search: '{search_query}'"
        msg += f"\n📄 Page {current_page + 1} of {total_pages}\n\n"

        for idx, player in enumerate(page_players, start_idx + 1):
            deposits = await self.get_user_deposits(player)
            total_deposits = sum(float(deposit.amount) for deposit in deposits)
            
            msg += f"{idx}. @{player.username}\n"
            msg += f"   • ID: {player.telegram_id}\n"
            msg += f"   • Joined: {player.created_at.strftime('%Y-%m-%d')}\n"
            msg += f"   • Total Deposits: {total_deposits:.2f} Birr\n\n"

        # Create inline keyboard for navigation
        keyboard = []
        
        # Search button
        keyboard.append([InlineKeyboardButton("🔍 Search Players", callback_data="search_players")])
        
        # Navigation buttons
        nav_buttons = []
        if current_page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"players_page_{current_page - 1}"))
        if current_page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"players_page_{current_page + 1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Back to menu button
        keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="agent_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)

        if hasattr(update, 'message'):
            await update.message.reply_text(msg, reply_markup=reply_markup)
        else:
            await update.edit_message_text(msg, reply_markup=reply_markup)
        return ConversationHandler.END

    async def agent_view_commission(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View agent's commission"""
        # Handle both regular updates and callback queries
        if hasattr(update, 'effective_user'):
            user_id = update.effective_user.id
        else:
            user_id = update.from_user.id
            
        # Get user and agent
        user = await self.get_or_create_user(user_id)
        agent = await self.get_agent_by_user(user)
        
        if not agent:
            reply_text = "❌ You are not registered as an agent. Use /register_agent to register."
            if hasattr(update, 'message'):
                await update.message.reply_text(reply_text)
            else:
                await update.edit_message_text(reply_text)
            return ConversationHandler.END

        # Get players and calculate stats
        players = await self.get_agent_players(agent)
        
        total_deposits = 0
        eligible_deposits = 0
        for player in players:
            deposits = await self.get_user_deposits(player)
            for deposit in deposits:
                amount = float(deposit.amount)
                total_deposits += amount
                if amount >= 100:
                    eligible_deposits += 1
        
        reply_text = (
            f"💸 Commission Report\n\n"
            f"💰 Total Earned: 0.00 Birr (Commission tracking not implemented)\n"
            f"👥 Total Players: {len(players)}\n"
            f"📊 Total Deposits: {total_deposits:.2f} Birr\n"
            f"✅ Eligible Deposits (≥100): {eligible_deposits}\n\n"
            f"💡 Commission tracking will be implemented in future updates"
        )
        
        if hasattr(update, 'message'):
            await update.message.reply_text(reply_text)
        else:
            await update.edit_message_text(reply_text)
        return ConversationHandler.END

    async def agent_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show agent menu"""
        user_id = update.effective_user.id
        
        # Get user and check if agent
        user = await self.get_or_create_user(user_id)
        agent = await self.get_agent_by_user(user)
        
        if not agent:
            await update.message.reply_text(
                "❌ You are not registered as an agent.\n"
                "Use /register_agent to register as an agent."
            )
            return
            
        keyboard = [
            [InlineKeyboardButton("👥 My Players", callback_data='view_players')],
            [InlineKeyboardButton("💸 My Commission", callback_data='view_commission')],
            [InlineKeyboardButton("📊 My Stats", callback_data='view_stats')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🎛️ Agent Menu:", reply_markup=reply_markup)

    async def handle_agent_menu_select(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle agent menu selections"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "view_players":
            await self.agent_view_players(query, context)
        elif query.data == "view_commission":
            await self.agent_view_commission(query, context)
        elif query.data == "view_stats":
            await self.agent_view_stats(query, context)
        elif query.data == "agent_menu":
            await self.agent_menu(query, context)
        elif query.data.startswith("players_page_"):
            # Handle pagination
            page = int(query.data.split("_")[-1])
            context.user_data['player_page'] = page
            await self.agent_view_players(query, context)
        elif query.data == "search_players":
            await self.handle_player_search(query, context)

    async def handle_player_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle player search request"""
        query = update.callback_query
        await query.answer()
        
        # Ask for search term
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="agent_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🔍 **Search Players**\n\n"
            "Please send me the search term. You can search by:\n"
            "• Username\n"
            "• Telegram ID\n"
            "• First name\n\n"
            "Type your search term or send 'clear' to show all players.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Set state to wait for search input
        context.user_data['waiting_for_search'] = True
        return ConversationHandler.END

    async def handle_search_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle search input from user"""
        if not context.user_data.get('waiting_for_search'):
            return ConversationHandler.END
            
        search_term = update.message.text.strip()
        
        if search_term.lower() == 'clear':
            context.user_data['player_search'] = ''
            context.user_data['player_page'] = 0
        else:
            context.user_data['player_search'] = search_term
            context.user_data['player_page'] = 0
        
        context.user_data['waiting_for_search'] = False
        
        # Show players with search results
        await self.agent_view_players(update, context)
        return ConversationHandler.END

    async def agent_view_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View agent statistics"""
        # Handle both regular updates and callback queries
        if hasattr(update, 'effective_user'):
            user_id = update.effective_user.id
        else:
            user_id = update.from_user.id
            
        # Get user and agent
        user = await self.get_or_create_user(user_id)
        agent = await self.get_agent_by_user(user)
        
        if not agent:
            reply_text = "❌ You are not registered as an agent."
            if hasattr(update, 'message'):
                await update.message.reply_text(reply_text)
            else:
                await update.edit_message_text(reply_text)
            return

        # Get players and calculate detailed stats
        players = await self.get_agent_players(agent)
        
        total_deposits = 0
        deposit_count = 0
        eligible_deposits = 0
        active_players = 0
        
        for player in players:
            deposits = await self.get_user_deposits(player)
            if deposits:
                active_players += 1
            for deposit in deposits:
                amount = float(deposit.amount)
                total_deposits += amount
                deposit_count += 1
                if amount >= 100:
                    eligible_deposits += 1
        
        avg_deposit = total_deposits / deposit_count if deposit_count > 0 else 0
        
        stats_text = f"""
📊 Agent Statistics

👤 Agent Info:
• Username: @{agent.user.username}
• Agent ID: {agent.referral_code}
• Registered: {agent.created_at.strftime('%Y-%m-%d')}

👥 Player Stats:
• Total Players: {len(players)}
• Active Players: {active_players}

💰 Financial Stats:
• Total Deposits: {total_deposits:.2f} Birr
• Deposit Count: {deposit_count}
• Average Deposit: {avg_deposit:.2f} Birr
• Eligible Deposits: {eligible_deposits}
• Commission Earned: 0.00 Birr (Not implemented)

🔗 Invite Link:
https://t.me/{context.bot.username}?start=ref_{agent.referral_code}
        """
        
        if hasattr(update, 'message'):
            await update.message.reply_text(stats_text)
        else:
            await update.edit_message_text(stats_text)

    async def my_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View user's statistics (player or agent)"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        # Get user
        user = await self.get_or_create_user(user_id, username)
        
        # Check if user is an agent
        agent = await self.get_agent_by_user(user)
        
        # Check if user is a player (has referrer)
        is_player = user.referred_by is not None
        
        if agent and is_player:
            # User is both agent and player
            deposits = await self.get_user_deposits(user)
            total_deposits = sum(float(deposit.amount) for deposit in deposits)
            
            stats_text = f"""
📊 Your Statistics (@{username})

👥 As Agent:
• Agent ID: {agent.referral_code}
• Players: {len(await self.get_agent_players(agent))}
• Commission: 0.00 Birr (Not implemented)

👤 As Player:
• Player ID: {user_id}
• Invited by: @{user.referred_by.username if user.referred_by else 'Unknown'}
• Joined: {user.created_at.strftime('%Y-%m-%d')}
• Deposits: {total_deposits:.2f} Birr
            """
        elif agent:
            # User is only an agent
            players = await self.get_agent_players(agent)
            stats_text = f"""
📊 Your Statistics (@{username})

👥 Agent Profile:
• Agent ID: {agent.referral_code}
• Players: {len(players)}
• Commission: 0.00 Birr (Not implemented)
• Registered: {agent.created_at.strftime('%Y-%m-%d')}

🔗 Invite Link:
https://t.me/{context.bot.username}?start=ref_{agent.referral_code}
            """
        elif is_player:
            # User is only a player
            deposits = await self.get_user_deposits(user)
            total_deposits = sum(float(deposit.amount) for deposit in deposits)
            
            stats_text = f"""
📊 Your Statistics (@{username})

👤 Player Profile:
• Player ID: {user_id}
• Invited by: @{user.referred_by.username if user.referred_by else 'Unknown'}
• Joined: {user.created_at.strftime('%Y-%m-%d')}
• Total Deposits: {total_deposits:.2f} Birr
• Deposit Count: {len(deposits)}
            """
        else:
            # User is neither
            stats_text = f"""
📊 Your Statistics (@{username})

❌ You are not registered as an agent or player.

💡 Available options:
• Use /register_agent to become an agent
• Use an invite link to join as a player
            """
        
        await update.message.reply_text(stats_text)

    async def record_deposit(self, user: User, amount: float):
        """Record a deposit and calculate commission"""
        if not user.referred_by:
            return False
            
        # Find the agent who referred this user
        agent = await self.get_agent_by_user(user.referred_by)
        if not agent:
            return False
            
        # If deposit >= 100, pay commission to the agent
        if amount >= 100:
            await self.update_agent_commission(agent, 1.0)
            return True
            
        return False

    async def deposit_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Simulate a deposit (for testing purposes)"""
        user_id = update.effective_user.id
        
        # Get user
        user = await self.get_or_create_user(user_id)
        
        if not user.referred_by:
            await update.message.reply_text(
                "❌ You are not registered as a player. Use an invite link to join first."
            )
            return
            
        if not context.args or len(context.args) == 0:
            await update.message.reply_text(
                "Usage: /deposit <amount>\nExample: /deposit 150"
            )
            return
            
        try:
            amount = float(context.args[0])
            if amount <= 0:
                await update.message.reply_text("❌ Amount must be positive.")
                return
                
            commission_earned = await self.record_deposit(user, amount)
            
            message = f"✅ Deposit recorded: {amount:.2f} Birr"
            if commission_earned:
                message += f"\n🎉 Your agent earned 1 Birr commission!"
                
            await update.message.reply_text(message)
            
        except ValueError:
            await update.message.reply_text("❌ Invalid amount. Please enter a number.")

    def setup_handlers(self):
        """Setup all bot handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("register_agent", self.agent_register))
        self.application.add_handler(CommandHandler("agent_menu", self.agent_menu))
        self.application.add_handler(CommandHandler("my_stats", self.my_stats))
        self.application.add_handler(CommandHandler("deposit", self.deposit_command))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(
            self.handle_agent_menu_select, 
            pattern="^(view_players|view_commission|view_stats|agent_menu|search_players|players_page_\d+)$"
        ))
        
        # Add message handler for search input
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_search_input
        ))
        
        # Set bot commands
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help message"),
            BotCommand("register_agent", "Register as an agent"),
            BotCommand("agent_menu", "Open agent menu"),
            BotCommand("my_stats", "View your statistics"),
            BotCommand("deposit", "Simulate a deposit (testing)"),
        ]
        
        async def post_init(application):
            await application.bot.set_my_commands(commands)
            
        self.application.post_init = post_init

    def run(self):
        """Run the bot"""
        logger.info("Starting Agent Bot...")
        self.application.run_polling()

def main():
    """Main function to run the standalone agent bot"""
    # Load environment variables from config file
    try:
        from decouple import config
        config_file = Path(__file__).parent / "config.env"
        if config_file.exists():
            os.environ.setdefault('DECOUPLE_CONFIG_FILE', str(config_file))
    except ImportError:
        pass  # decouple not available, use environment variables only
    
    # Get bot token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN') or "8154094611:AAFF2uibjzso6VHqGkgEtf17l1L7MnOZ1nY"
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
        sys.exit(1)
    
    # Create and run the bot
    bot = AgentBot(token)
    
    try:
        # Simple approach - just run the bot (no asyncio.run needed)
        logger.info("Starting bot...")
        bot.run()
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
