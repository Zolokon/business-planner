"""
Voice Message Handler - Business Planner.

Handles voice messages and converts them to tasks using LangGraph workflow.

Reference:
- ADR-001 (LangGraph)
- ADR-007 (Telegram Architecture)
- docs/05-ai-specifications/langgraph-flows.md
"""

from telegram import Update
from telegram.ext import ContextTypes

from src.utils.logger import logger
from src.infrastructure.database import get_session
from src.ai.graphs.voice_task_creation import process_voice_message


# ============================================================================
# Voice Message Handler
# ============================================================================

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice message from user.
    
    Workflow:
    1. Download voice message from Telegram
    2. Send to LangGraph workflow (voice_task_creation)
    3. Return formatted response to user
    
    Args:
        update: Telegram update with voice message
        context: Bot context
        
    Reference: docs/05-ai-specifications/langgraph-flows.md (Voice Task Creation)
    """
    
    if not update.message or not update.message.voice:
        return
    
    user = update.effective_user
    chat_id = update.effective_chat.id
    voice = update.message.voice
    
    logger.info(
        "voice_message_received",
        user_id=user.id,
        username=user.username,
        duration=voice.duration,
        file_size=voice.file_size
    )
    
    # Check voice duration (ADR-007: max 5 minutes)
    if voice.duration > 300:
        await update.message.reply_text(
            "❌ Голосовое сообщение слишком длинное (макс. 5 минут).\n"
            "Пожалуйста, запишите короче."
        )
        return
    
    # Send "processing" indicator
    await update.message.reply_chat_action("typing")
    
    try:
        # Download voice file
        voice_file = await context.bot.get_file(voice.file_id)
        voice_bytes = await voice_file.download_as_bytearray()
        
        logger.info(
            "voice_downloaded",
            user_id=user.id,
            size_bytes=len(voice_bytes)
        )
        
        # Process through LangGraph workflow
        session_gen = get_session()
        session = await anext(session_gen)
        try:
            result = await process_voice_message(
                audio_bytes=bytes(voice_bytes),
                audio_duration=voice.duration,
                user_id=user.id,  # TODO: Map Telegram user to DB user
                telegram_chat_id=chat_id,
                session=session
            )
        finally:
            await session.close()
        
        # Send response
        response = result.get("telegram_response", "❌ Ошибка обработки")
        
        # Add inline buttons if task created successfully
        if result.get("created_task_id"):
            from telegram import InlineKeyboardButton, InlineKeyboardMarkup
            
            task_id = result["created_task_id"]
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ Завершить", callback_data=f"complete:{task_id}"),
                    InlineKeyboardButton("✏️ Изменить", callback_data=f"edit:{task_id}")
                ],
                [
                    InlineKeyboardButton("📅 Перенести", callback_data=f"reschedule:{task_id}"),
                    InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete:{task_id}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                response,
                reply_markup=reply_markup
            )
        else:
            # Error message, no buttons
            await update.message.reply_text(response)
        
        logger.info(
            "voice_processed_successfully",
            user_id=user.id,
            task_id=result.get("created_task_id"),
            processing_time_ms=result.get("processing_time_ms")
        )
        
    except Exception as e:
        logger.error(
            "voice_processing_failed",
            user_id=user.id,
            error=str(e),
            exc_info=True
        )
        
        await update.message.reply_text(
            "❌ Произошла ошибка при обработке голосового сообщения.\n"
            "Попробуйте еще раз или напишите задачу текстом через /task"
        )


# ============================================================================
# Voice Message Helpers
# ============================================================================

async def convert_voice_to_ogg(voice_bytes: bytes) -> bytes:
    """Convert voice message to OGG format (if needed).
    
    Telegram sends voice in OGG/OPUS format, which Whisper accepts.
    This is a placeholder if conversion is needed.
    
    Args:
        voice_bytes: Raw voice bytes from Telegram
        
    Returns:
        Converted voice bytes (OGG format)
    """
    
    # Telegram already sends OGG/OPUS, no conversion needed
    return voice_bytes

