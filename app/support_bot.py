"""
Standalone Support Bot

Purpose:
- Provide a Telegram bot for internal support operations with role-based access control (RBAC).
- Roles enforced using Django user model flags and groups: superuser, admin (is_staff), Support, Finance.

How to run:
  1) Ensure DJANGO_SETTINGS_MODULE=core.settings is available in env
  2) Set SUPPORT_BOT_TOKEN in environment (or .env)
  3) python support_bot.py

Notes:
- Uses python-telegram-bot v20+ style handlers
- Commands are read-only by default; write/approve actions restricted to Admin/Finance
"""

import os
import asyncio
import logging
from typing import Callable

import django
from decouple import config


# Django setup for standalone execution
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.db.models import Q
from wallet.models import WithdrawalRequest, PaymentSettings, Wallet, Transaction
from users.models import User as UserModel  # explicit for clarity
from asgiref.sync import sync_to_async

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from telegram.constants import ParseMode
from telegram import BotCommand
from telegram.error import NetworkError, RetryAfter, TimedOut
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("support_bot")


def user_has_any_role(dj_user: UserModel, roles: list[str]) -> bool:
    roles_l = [r.lower() for r in roles]
    if "superuser" in roles_l and dj_user.is_superuser:
        return True
    if "admin" in roles_l and dj_user.is_staff:
        return True
    if any(dj_user.groups.filter(name__iexact=r).exists() for r in roles):
        return True
    return False


def role_required(*roles: str) -> Callable:
    """Decorator for telegram command handlers to enforce RBAC based on Django user roles.

    Roles can be: 'superuser', 'admin', 'Support', 'Finance', etc. (group names are case-insensitive)
    """

    def decorator(func: Callable):
        normalized = [r.lower() for r in roles]
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            telegram_id = update.effective_user.id if update.effective_user else None
            if telegram_id is None:
                await update.effective_message.reply_text("Unauthorized: missing user.")
                return
            try:
                dj_user = await sync_to_async(get_user_model().objects.get, thread_sensitive=True)(telegram_id=str(telegram_id))
            except get_user_model().DoesNotExist:
                await update.effective_message.reply_text("Unauthorized: your Telegram ID is not linked to a user.")
                return

            # Fast checks for flags
            if "superuser" in normalized and dj_user.is_superuser:
                return await func(update, context)
            if "admin" in normalized and dj_user.is_staff:
                return await func(update, context)

            # Check groups asynchronously
            group_names = await sync_to_async(lambda: list(dj_user.groups.values_list("name", flat=True)), thread_sensitive=True)()
            group_names_l = [g.lower() for g in group_names]
            if any(g in normalized for g in group_names_l):
                return await func(update, context)

            await update.effective_message.reply_text("You don't have permission to run this command.")
            return

        return wrapper

    return decorator


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update, context)


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "Support Bot Commands\n\n"
        "General:\n"
        "  /whoami - show your mapped user and roles\n"
        "  /payment_settings - view payment settings\n\n"
        "Finance/Admin:\n"
        "  /wr_pending - list pending withdrawal requests\n"
        "  /wr_approve <id> - approve withdrawal request\n"
        "  /wr_reject <id> - reject withdrawal request\n\n"
        "Support/Admin:\n"
        "  /user_search <query> - search users by username/phone/telegram_id\n"
        "  /user_wallet <user_id> - show wallet and summary\n"
    )
    await update.effective_message.reply_text(msg)


def build_main_menu(dj_user: UserModel | None):
    rows = []
    rows.append([InlineKeyboardButton("👤 Who am I", callback_data="menu_whoami")])
    rows.append([InlineKeyboardButton("⚙️ Payment Settings", callback_data="menu_payment_settings")])
    rows.append([
        InlineKeyboardButton("⏳ Pending Withdrawals", callback_data="menu_wr_pending"),
    ])
    rows.append([
        InlineKeyboardButton("🔎 User Search", callback_data="menu_user_search"),
        InlineKeyboardButton("👛 User Wallet", callback_data="menu_user_wallet"),
    ])
    return InlineKeyboardMarkup(rows)


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id if update.effective_user else None
    dj_user = None
    if tg_id:
        try:
            dj_user = await sync_to_async(get_user_model().objects.get, thread_sensitive=True)(telegram_id=str(tg_id))
        except Exception:
            dj_user = None
    try:
        await update.effective_message.reply_text(
            "🔧 Support Bot\nChoose an action:", reply_markup=build_main_menu(dj_user)
        )
    except (NetworkError, RetryAfter, TimedOut):
        await asyncio.sleep(1)
        try:
            await update.effective_message.reply_text(
                "🔧 Support Bot\nChoose an action:", reply_markup=build_main_menu(dj_user)
            )
        except Exception as e:
            logger.warning(f"Failed to send main menu: {e}")


@role_required("Finance", "admin", "superuser")
async def prompt_wr_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Shown from menu_wr_pending
    reqs = await sync_to_async(
        lambda: list(WithdrawalRequest.objects.filter(status="pending").select_related("user").order_by("-created_at")[:10]),
        thread_sensitive=True,
    )()
    if not reqs:
        await update.effective_message.reply_text("No pending withdrawal requests.")
        return
    rows = []
    for r in reqs:
        rows.append([
            InlineKeyboardButton(f"#{r.id} {r.user.username} ETB {r.amount}", callback_data=f"wr_show_{r.id}")
        ])
    rows.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_root")])
    await update.effective_message.reply_text("Select a request:", reply_markup=InlineKeyboardMarkup(rows))


@role_required("Support", "admin", "superuser")
async def prompt_user_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.effective_message.reply_text(
            "Send search query (username/phone/telegram_id):",
            reply_markup=ForceReply(selective=True)
        )
    except (NetworkError, RetryAfter, TimedOut):
        await asyncio.sleep(1)
        try:
            await update.effective_message.reply_text(
                "Send search query (username/phone/telegram_id):",
                reply_markup=ForceReply(selective=True)
            )
        except Exception as e:
            logger.warning(f"Failed to prompt user search: {e}")
    context.chat_data['awaiting'] = 'user_search_query'


@role_required("Support", "admin", "superuser")
async def prompt_user_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.effective_message.reply_text(
            "Send user id to view wallet:", reply_markup=ForceReply(selective=True)
        )
    except (NetworkError, RetryAfter, TimedOut):
        await asyncio.sleep(1)
        try:
            await update.effective_message.reply_text(
                "Send user id to view wallet:", reply_markup=ForceReply(selective=True)
            )
        except Exception as e:
            logger.warning(f"Failed to prompt user wallet: {e}")
    context.chat_data['awaiting'] = 'user_wallet_id'


async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    try:
        u: UserModel = await sync_to_async(get_user_model().objects.get, thread_sensitive=True)(telegram_id=str(tg_id))
        groups = await sync_to_async(lambda: list(u.groups.values_list("name", flat=True)), thread_sensitive=True)()
        roles = []
        if u.is_superuser:
            roles.append("superuser")
        if u.is_staff:
            roles.append("admin")
        roles.extend(groups)
        text = (
            f"User: {u.username} (id={u.id})\n"
            f"Phone: {u.phone}\n"
            f"Roles: {', '.join(roles) if roles else 'none'}\n"
        )
    except get_user_model().DoesNotExist:
        text = "Your Telegram ID is not linked to any user."
    await update.effective_message.reply_text(text)


@role_required("Finance", "admin", "superuser")
async def payment_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        ps = await sync_to_async(PaymentSettings.get_solo, thread_sensitive=True)()
        msg = (
            "Payment Settings:\n"
            f"- Min Deposit: {ps.min_deposit_amount}\n"
            f"- Min Withdrawal: {ps.min_withdrawal_amount}\n"
            f"- Max Withdrawal: {ps.max_withdrawal_amount}\n"
            f"- Withdrawal Fee %: {ps.withdrawal_fee_percent}\n"
        )
    except Exception as e:
        msg = f"Error loading settings: {e}"
    await update.effective_message.reply_text(msg)


@role_required("Finance", "admin", "superuser")
async def wr_pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reqs = await sync_to_async(
        lambda: list(WithdrawalRequest.objects.filter(status="pending").select_related("user").order_by("-created_at")[:20]),
        thread_sensitive=True,
    )()
    if not reqs:
        await update.effective_message.reply_text("No pending withdrawal requests.")
        return
    lines = [
        "Pending Withdrawal Requests (top 20):",
    ]
    for r in reqs:
        lines.append(
            f"#{r.id} | user={r.user.username}({r.user.id}) | amt={r.amount} | at={r.created_at:%Y-%m-%d %H:%M}"
        )
    await update.effective_message.reply_text("\n".join(lines))
    # Offer inline navigation for actions
    rows = [[InlineKeyboardButton("Manage", callback_data="menu_wr_pending")], [InlineKeyboardButton("⬅️ Back", callback_data="menu_root")]]
    await update.effective_message.reply_text("Choose:", reply_markup=InlineKeyboardMarkup(rows))


@role_required("Finance", "admin", "superuser")
async def wr_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("Usage: /wr_approve <id>")
        return
    try:
        req_id = int(context.args[0])
        req = await sync_to_async(WithdrawalRequest.objects.select_related("user").get, thread_sensitive=True)(id=req_id)
    except Exception:
        await update.effective_message.reply_text("Invalid withdrawal request id.")
        return

    if req.status != "pending":
        await update.effective_message.reply_text(f"Request #{req.id} is already {req.status}.")
        return

    # Mark approved; business payout flow remains manual/off-bot
    req.status = "approved"
    await sync_to_async(req.save, thread_sensitive=True)(update_fields=["status", "updated_at"])
    await update.effective_message.reply_text(f"✅ Approved withdrawal request #{req.id} for {req.user.username} ({req.amount} ETB)")


@role_required("Finance", "admin", "superuser")
async def wr_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("Usage: /wr_reject <id>")
        return
    try:
        req_id = int(context.args[0])
        req = await sync_to_async(WithdrawalRequest.objects.select_related("user").get, thread_sensitive=True)(id=req_id)
    except Exception:
        await update.effective_message.reply_text("Invalid withdrawal request id.")
        return

    if req.status != "pending":
        await update.effective_message.reply_text(f"Request #{req.id} is already {req.status}.")
        return

    req.status = "rejected"
    await sync_to_async(req.save, thread_sensitive=True)(update_fields=["status", "updated_at"])
    await update.effective_message.reply_text(f"❌ Rejected withdrawal request #{req.id} for {req.user.username} ({req.amount} ETB)")


@role_required("Support", "admin", "superuser")
async def user_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("Usage: /user_search <username|phone|telegram_id>")
        return
    q = " ".join(context.args).strip()
    users = await sync_to_async(
        lambda: list(
            get_user_model()
            .objects.filter(
                Q(username__icontains=q) | Q(phone__icontains=q) | Q(telegram_id__icontains=q)
            )
            .order_by("id")[:10]
        ),
        thread_sensitive=True,
    )()
    if not users:
        await update.effective_message.reply_text("No users found.")
        return
    lines = ["Users:"]
    for u in users:
        lines.append(f"{u.id} | {u.username} | {u.phone} | tg={u.telegram_id}")
    await update.effective_message.reply_text("\n".join(lines))


@role_required("Support", "admin", "superuser")
async def user_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.effective_message.reply_text("Usage: /user_wallet <user_id>")
        return
    try:
        uid = int(context.args[0])
        u = await sync_to_async(get_user_model().objects.get, thread_sensitive=True)(id=uid)
    except Exception:
        await update.effective_message.reply_text("Invalid user id")
        return

    async def _collect():
        def _sync():
            wallet = Wallet.objects.filter(user=u).first()
            deposits = Transaction.objects.filter(user=u, type='DEPOSIT').count()
            withdrawals = Transaction.objects.filter(user=u, type='WITHDRAW').count()
            bets = Transaction.objects.filter(user=u, type='BET').count()
            wins = Transaction.objects.filter(user=u, type='WIN').count()
            return wallet, deposits, withdrawals, bets, wins
        return await sync_to_async(_sync, thread_sensitive=True)()

    wallet, deposits, withdrawals, bets, wins = await _collect()

    msg = (
        f"User: {u.username} (id={u.id})\n"
        f"Phone: {u.phone}\n"
        f"Balance: {getattr(wallet, 'balance', 0.0)}\n"
        f"Tx counts - deposits: {deposits}, withdrawals: {withdrawals}, bets: {bets}, wins: {wins}"
    )
    await update.effective_message.reply_text(msg)


async def main():
    token = config("SUPPORT_BOT_TOKEN", default=os.getenv("SUPPORT_BOT_TOKEN", ""))
    if not token:
        raise RuntimeError("SUPPORT_BOT_TOKEN is not configured")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("whoami", whoami))
    app.add_handler(CommandHandler("menu", show_main_menu))

    # Finance/Admin
    app.add_handler(CommandHandler("payment_settings", payment_settings))
    app.add_handler(CommandHandler("wr_pending", wr_pending))
    app.add_handler(CommandHandler("wr_approve", wr_approve))
    app.add_handler(CommandHandler("wr_reject", wr_reject))

    # Support/Admin
    app.add_handler(CommandHandler("user_search", user_search))
    app.add_handler(CommandHandler("user_wallet", user_wallet))

    # Interactive prompts
    app.add_handler(CallbackQueryHandler(lambda u,c: show_main_menu(u,c), pattern="^menu_root$"))
    app.add_handler(CallbackQueryHandler(lambda u,c: whoami(u,c), pattern="^menu_whoami$"))
    app.add_handler(CallbackQueryHandler(lambda u,c: payment_settings(u,c), pattern="^menu_payment_settings$"))
    app.add_handler(CallbackQueryHandler(lambda u,c: prompt_wr_action(u,c), pattern="^menu_wr_pending$"))
    app.add_handler(CallbackQueryHandler(lambda u,c: prompt_user_search(u,c), pattern="^menu_user_search$"))
    app.add_handler(CallbackQueryHandler(lambda u,c: prompt_user_wallet(u,c), pattern="^menu_user_wallet$"))

    # ForceReply handlers
    async def on_text_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
        awaiting = context.chat_data.get('awaiting')
        if awaiting == 'user_search_query':
            # transform to args and call user_search
            context.args = [update.effective_message.text]
            context.chat_data['awaiting'] = None
            return await user_search(update, context)
        if awaiting == 'user_wallet_id':
            context.args = [update.effective_message.text]
            context.chat_data['awaiting'] = None
            return await user_wallet(update, context)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text_reply))

    await app.initialize()

    # Set static commands for bottom-left menu
    commands = [
        BotCommand("menu", "Open main menu"),
        BotCommand("whoami", "Show my roles"),
        BotCommand("payment_settings", "View payment settings"),
        BotCommand("wr_pending", "List pending withdrawals"),
        BotCommand("wr_approve", "Approve withdrawal: /wr_approve <id>"),
        BotCommand("wr_reject", "Reject withdrawal: /wr_reject <id>"),
        BotCommand("user_search", "Search users: /user_search <query>"),
        BotCommand("user_wallet", "User wallet: /user_wallet <id>")
    ]
    try:
        await app.bot.set_my_commands(commands)
    except Exception as e:
        logger.warning(f"Failed to set bot commands: {e}")

    # Global error handler to prevent noisy stack traces
    async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.error("Unhandled error", exc_info=context.error)

    app.add_error_handler(on_error)
    await app.start()
    logger.info("Support bot started")
    try:
        await app.updater.start_polling()
        await asyncio.Event().wait()
    finally:
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass


