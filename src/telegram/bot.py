"""
Telegram Bot Client - Business Planner.

Main bot setup and initialization.

Reference:
- ADR-007 (Telegram Architecture)
- docs/03-api/telegram-commands.md
"""

import asyncio
from typing import TYPE_CHECKING

from telegram import Bot, BotCommand
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from src.config import settings
from src.utils.logger import logger

if TYPE_CHECKING:
    from telegram.ext import Application as TelegramApplication


# ============================================================================
# Bot Commands Definition
# ============================================================================

BOT_COMMANDS = [
    BotCommand("start", "Начать работу с ботом"),
    BotCommand("today", "Задачи на сегодня"),
    BotCommand("week", "Задачи на неделю"),
    BotCommand("task", "Создать задачу текстом"),
    BotCommand("complete", "Завершить задачу"),
    BotCommand("weekly", "Недельная аналитика (по пятницам)"),
    BotCommand("help", "Помощь по командам")
]


# ============================================================================
# Bot Initialization
# ============================================================================

def create_bot_application() -> "TelegramApplication":
    """Create and configure Telegram bot application.
    
    Sets up:
    - Bot client with token
    - Command handlers
    - Message handlers (voice, text)
    - Callback query handlers (inline buttons)
    - Error handler
    
    Returns:
        Configured Application instance
        
    Reference: ADR-007 (Webhook strategy)
    """
    
    logger.info("creating_telegram_bot_application")
    
    # Build application
    app = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .build()
    )
    
    # Import handlers (lazy to avoid circular imports)
    from src.telegram.handlers.command_handler import (
        start_command,
        today_command,
        week_command,
        task_command,
        complete_command,
        weekly_command,
        help_command
    )
    from src.telegram.handlers.voice_handler import handle_voice_message
    from src.telegram.handlers.callback_handler import handle_callback_query
    from src.telegram.handlers.error_handler import handle_error
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("today", today_command))
    app.add_handler(CommandHandler("week", week_command))
    app.add_handler(CommandHandler("task", task_command))
    app.add_handler(CommandHandler("complete", complete_command))
    app.add_handler(CommandHandler("weekly", weekly_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Add message handlers
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    
    # Add callback query handler (inline buttons)
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Add error handler
    app.add_error_handler(handle_error)
    
    logger.info("telegram_bot_application_created")
    
    return app


async def setup_bot_commands(bot: Bot) -> None:
    """Set bot commands (displayed in Telegram menu).
    
    Args:
        bot: Telegram Bot instance
        
    Reference: docs/03-api/telegram-commands.md
    """
    
    try:
        await bot.set_my_commands(BOT_COMMANDS)
        logger.info("bot_commands_set", commands_count=len(BOT_COMMANDS))
    except Exception as e:
        logger.error("failed_to_set_bot_commands", error=str(e))


async def setup_webhook(app: "TelegramApplication") -> None:
    """Setup webhook for production (Digital Ocean).
    
    In development, use long polling instead.
    
    Args:
        app: Telegram Application
        
    Reference: ADR-007 (Webhook vs Polling)
    """
    
    if not settings.telegram_use_webhook:
        logger.info("webhook_disabled_using_polling")
        return
    
    webhook_url = settings.telegram_webhook_url
    secret_token = settings.telegram_secret_token
    
    try:
        await app.bot.set_webhook(
            url=webhook_url,
            secret_token=secret_token,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True  # Clear old updates on restart
        )
        
        logger.info(
            "webhook_configured",
            url=webhook_url,
            secret_token_set=bool(secret_token)
        )
        
    except Exception as e:
        logger.error("webhook_setup_failed", error=str(e))
        raise


async def remove_webhook(app: "TelegramApplication") -> None:
    """Remove webhook (cleanup on shutdown).
    
    Args:
        app: Telegram Application
    """
    
    try:
        await app.bot.delete_webhook()
        logger.info("webhook_removed")
    except Exception as e:
        logger.warning("webhook_removal_failed", error=str(e))


# ============================================================================
# Bot Lifecycle (for standalone mode)
# ============================================================================

async def start_bot_polling(app: "TelegramApplication") -> None:
    """Start bot in polling mode (development).
    
    Args:
        app: Telegram Application
    """
    
    logger.info("starting_bot_polling_mode")
    
    # Set commands
    await setup_bot_commands(app.bot)
    
    # Initialize application
    await app.initialize()
    await app.start()
    
    # Start polling
    await app.updater.start_polling(
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True
    )
    
    logger.info("bot_polling_started")


async def stop_bot_polling(app: "TelegramApplication") -> None:
    """Stop bot polling mode (development).
    
    Args:
        app: Telegram Application
    """
    
    logger.info("stopping_bot_polling")
    
    if app.updater.running:
        await app.updater.stop()
    
    await app.stop()
    await app.shutdown()
    
    logger.info("bot_polling_stopped")


# ============================================================================
# Standalone Bot Runner (for testing)
# ============================================================================

async def run_bot_standalone():
    """Run bot as standalone application (development/testing).
    
    Usage:
        python -m src.telegram.bot
    """
    
    logger.info("starting_standalone_bot")
    
    app = create_bot_application()
    
    try:
        await start_bot_polling(app)
        
        # Keep running
        logger.info("bot_running_press_ctrl_c_to_stop")
        await asyncio.Event().wait()  # Wait forever
        
    except KeyboardInterrupt:
        logger.info("received_shutdown_signal")
    finally:
        await stop_bot_polling(app)
        logger.info("bot_stopped")


if __name__ == "__main__":
    # Run standalone bot
    asyncio.run(run_bot_standalone())

