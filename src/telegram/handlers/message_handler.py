"""
Text Message Handler - Business Planner.

Handles plain text messages for task editing.

Reference: ADR-007 (Telegram Architecture)
"""

from telegram import Update
from telegram.ext import ContextTypes

from src.utils.logger import logger
from src.infrastructure.database import get_session
from src.infrastructure.database.repositories.task_repository import TaskRepository
from src.domain.models import TaskUpdate
from src.domain.constants import BUSINESS_NAMES, PRIORITY_NAMES


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text message from user.

    Currently used for:
    - Editing task title

    Args:
        update: Telegram update with text message
        context: Bot context
    """

    if not update.message or not update.message.text:
        return

    user = update.effective_user
    text = update.message.text.strip()

    # Check if user is editing a task
    if "editing_task_id" in context.user_data and "editing_field" in context.user_data:
        task_id = context.user_data["editing_task_id"]
        field = context.user_data["editing_field"]

        if field == "title":
            await handle_title_update(update, context, task_id, text)
            return

        if field == "transcript":
            await handle_transcript_update(update, context, task_id, text)
            return

    # No active editing session - ignore message
    # (Voice messages are handled separately, commands too)
    logger.debug("text_message_ignored", user_id=user.id, text_length=len(text))


async def handle_title_update(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    task_id: int,
    new_title: str
) -> None:
    """Update task title.

    Args:
        update: Telegram update
        context: Bot context
        task_id: Task ID to update
        new_title: New title
    """

    user = update.effective_user

    logger.info("updating_task_title", user_id=user.id, task_id=task_id)

    try:
        # Validate title length
        if len(new_title) < 1:
            await update.message.reply_text("❌ Название не может быть пустым")
            return

        if len(new_title) > 500:
            await update.message.reply_text("❌ Название слишком длинное (макс. 500 символов)")
            return

        # Update in database
        async with get_session() as session:
            repo = TaskRepository(session)

            task_update = TaskUpdate(title=new_title)
            updated_task = await repo.update(task_id, task_update)

        # Clear editing context
        context.user_data.pop("editing_task_id", None)
        context.user_data.pop("editing_field", None)

        # Send confirmation
        await update.message.reply_text(
            f"✅ **Название обновлено!**\n\n"
            f"Задача #{task_id}:\n"
            f"📝 {updated_task.title}"
        )

        logger.info("task_title_updated", task_id=task_id, user_id=user.id)

    except Exception as e:
        logger.error("task_title_update_failed", task_id=task_id, error=str(e))
        await update.message.reply_text("❌ Ошибка при обновлении названия")


async def handle_transcript_update(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    task_id: int,
    new_transcript: str
) -> None:
    """Update task from edited transcript - re-parses and updates task.

    Args:
        update: Telegram update
        context: Bot context
        task_id: Task ID to update
        new_transcript: Corrected transcript text
    """
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    from datetime import datetime

    from src.ai.parsers.task_parser import parse_task_from_transcript

    user = update.effective_user

    logger.info("updating_task_transcript", user_id=user.id, task_id=task_id)

    # Send processing indicator
    await update.message.reply_chat_action("typing")

    try:
        # Validate transcript
        if len(new_transcript) < 3:
            await update.message.reply_text("❌ Текст слишком короткий")
            return

        if len(new_transcript) > 2000:
            await update.message.reply_text("❌ Текст слишком длинный (макс. 2000 символов)")
            return

        # Get existing task to get user_id
        session_gen = get_session()
        session = await anext(session_gen)
        try:
            repo = TaskRepository(session)

            existing_task = await repo.get_by_id(task_id)
            if not existing_task:
                await update.message.reply_text(f"❌ Задача #{task_id} не найдена")
                return

            # Re-parse transcript with AI
            parsed = await parse_task_from_transcript(
                transcript=new_transcript,
                user_id=existing_task.user_id
            )

            # Convert deadline if present
            deadline = None
            if parsed.deadline:
                try:
                    deadline = datetime.fromisoformat(parsed.deadline)
                except (ValueError, TypeError):
                    pass

            # Update task with parsed data
            task_update = TaskUpdate(
                title=parsed.title,
                priority=parsed.priority,
                deadline=deadline
            )

            updated_task = await repo.update(task_id, task_update)

            # Update metadata with new transcript
            metadata = await repo.get_metadata(task_id) or {}
            metadata["transcript"] = new_transcript
            metadata["transcript_edited"] = True
            await repo.update_metadata(task_id, metadata)

        finally:
            await session.close()

        # Clear editing context
        context.user_data.pop("editing_task_id", None)
        context.user_data.pop("editing_field", None)

        # Format response
        business_name = BUSINESS_NAMES.get(updated_task.business_id, "Неизвестный")
        priority_name = PRIORITY_NAMES.get(updated_task.priority, "Средний")
        deadline_text = updated_task.deadline.strftime("%d.%m.%Y") if updated_task.deadline else "не указан"

        # Build response message
        message = f"""ЗАДАЧА ОБНОВЛЕНА

{updated_task.title}

Бизнес:    {business_name}
Приоритет: {priority_name}
Дедлайн:   {deadline_text}"""

        # Add inline buttons
        keyboard = [
            [
                InlineKeyboardButton("Завершить", callback_data=f"complete:{task_id}"),
                InlineKeyboardButton("Изменить", callback_data=f"edit:{task_id}")
            ],
            [
                InlineKeyboardButton("Перенести", callback_data=f"reschedule:{task_id}"),
                InlineKeyboardButton("Удалить", callback_data=f"delete:{task_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(message, reply_markup=reply_markup)

        logger.info(
            "task_transcript_updated",
            task_id=task_id,
            user_id=user.id,
            new_title=updated_task.title
        )

    except Exception as e:
        logger.error("task_transcript_update_failed", task_id=task_id, error=str(e))
        await update.message.reply_text(
            "❌ Ошибка при обновлении задачи.\n"
            "Попробуйте еще раз или отредактируйте вручную."
        )
