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
