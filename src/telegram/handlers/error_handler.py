"""
Error Handler - Business Planner.

Global error handler for Telegram bot.

Reference: ADR-007 (Telegram Architecture - Error Handling)
"""

from telegram import Update
from telegram.ext import ContextTypes

from src.utils.logger import logger


# ============================================================================
# Error Handler
# ============================================================================

async def handle_error(update: Update | None, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the Telegram bot.
    
    This is a global error handler that catches all unhandled exceptions
    in command handlers, message handlers, and callback handlers.
    
    Args:
        update: Telegram update (may be None)
        context: Bot context with error information
        
    Reference: ADR-007 (Error handling strategy)
    """
    
    error = context.error
    
    # Log error with full context
    logger.error(
        "telegram_bot_error",
        error_type=type(error).__name__,
        error_message=str(error),
        update_type=type(update).__name__ if update else None,
        user_id=update.effective_user.id if update and update.effective_user else None,
        chat_id=update.effective_chat.id if update and update.effective_chat else None,
        exc_info=error
    )
    
    # Try to send error message to user
    if update and update.effective_message:
        try:
            error_message = _get_user_friendly_error_message(error)
            
            await update.effective_message.reply_text(
                f"❌ {error_message}\n\n"
                "Попробуйте еще раз или обратитесь к администратору."
            )
            
        except Exception as e:
            # Failed to send error message to user
            logger.error(
                "failed_to_send_error_message",
                error=str(e)
            )


# ============================================================================
# Error Message Mapping
# ============================================================================

def _get_user_friendly_error_message(error: Exception) -> str:
    """Convert technical error to user-friendly message.
    
    Args:
        error: Exception object
        
    Returns:
        User-friendly error message in Russian
    """
    
    error_type = type(error).__name__
    error_str = str(error).lower()
    
    # Network errors
    if "timeout" in error_str or "timed out" in error_str:
        return "Превышено время ожидания. Попробуйте еще раз."
    
    if "connection" in error_str or "network" in error_str:
        return "Проблема с подключением. Проверьте интернет."
    
    # OpenAI API errors
    if "openai" in error_str or "api" in error_str:
        return "Временная проблема с AI сервисом. Попробуйте через минуту."
    
    if "rate limit" in error_str:
        return "Слишком много запросов. Подождите немного."
    
    # Database errors
    if "database" in error_str or "psycopg" in error_str:
        return "Проблема с базой данных. Попробуйте позже."
    
    # Validation errors
    if "validation" in error_str:
        return "Неверный формат данных. Проверьте ввод."
    
    # Permission errors
    if "permission" in error_str or "forbidden" in error_str:
        return "Недостаточно прав для выполнения операции."
    
    # Not found errors
    if "not found" in error_str or "404" in error_str:
        return "Запрошенные данные не найдены."
    
    # Default error message
    return "Произошла непредвиденная ошибка"


# ============================================================================
# Error Recovery Strategies
# ============================================================================

async def retry_with_backoff(
    func,
    max_retries: int = 3,
    initial_delay: float = 1.0
) -> any:
    """Retry function with exponential backoff.
    
    Useful for transient errors (network, API rate limits).
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds
        
    Returns:
        Function result
        
    Raises:
        Last exception if all retries fail
    """
    
    import asyncio
    
    delay = initial_delay
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            last_error = e
            
            logger.warning(
                "retry_attempt",
                attempt=attempt + 1,
                max_retries=max_retries,
                delay=delay,
                error=str(e)
            )
            
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
    
    # All retries failed
    raise last_error

