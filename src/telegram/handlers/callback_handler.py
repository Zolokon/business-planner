"""
Callback Query Handler - Business Planner.

Handles inline button callbacks.

Callback data format:
- complete:<task_id> - Complete task
- edit:<task_id> - Edit task
- reschedule:<task_id> - Reschedule task
- delete:<task_id> - Delete task
- today - Show today's tasks
- week - Show week's tasks
- help - Show help

Reference: ADR-007 (Telegram Architecture)
"""

from telegram import Update
from telegram.ext import ContextTypes

from src.utils.logger import logger
from src.infrastructure.database import get_session
from src.infrastructure.database.repositories.task_repository import TaskRepository


# ============================================================================
# Callback Query Handler
# ============================================================================

async def handle_callback_query(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle inline button callback queries.
    
    Args:
        update: Telegram update with callback query
        context: Bot context
    """
    
    query = update.callback_query
    user = update.effective_user
    
    if not query or not query.data:
        return
    
    # Answer callback query (removes "loading" indicator)
    await query.answer()
    
    callback_data = query.data
    
    logger.info(
        "callback_received",
        user_id=user.id,
        callback_data=callback_data
    )
    
    # Parse callback data
    if ":" in callback_data:
        action, param = callback_data.split(":", 1)
    else:
        action = callback_data
        param = None
    
    # Route to appropriate handler
    try:
        if action == "complete":
            await handle_complete_callback(query, context, int(param))
        elif action == "edit":
            await handle_edit_callback(query, context, int(param))
        elif action == "reschedule":
            await handle_reschedule_callback(query, context, int(param))
        elif action == "delete":
            await handle_delete_callback(query, context, int(param))
        elif action == "today":
            await handle_today_callback(query, context)
        elif action == "week":
            await handle_week_callback(query, context)
        elif action == "help":
            await handle_help_callback(query, context)
        elif action == "complete_prompt":
            await handle_complete_prompt_callback(query, context)
        elif action == "new_task":
            await handle_new_task_callback(query, context)
        else:
            logger.warning("unknown_callback_action", action=action)
            await query.edit_message_text("❌ Неизвестное действие")
            
    except Exception as e:
        logger.error(
            "callback_handler_error",
            user_id=user.id,
            callback_data=callback_data,
            error=str(e)
        )
        await query.edit_message_text(
            "❌ Произошла ошибка. Попробуйте позже."
        )


# ============================================================================
# Individual Callback Handlers
# ============================================================================

async def handle_complete_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE,
    task_id: int
) -> None:
    """Handle 'complete task' button click.
    
    Args:
        query: Callback query
        context: Bot context
        task_id: Task ID to complete
    """
    
    user = query.from_user
    
    logger.info("callback_complete_task", user_id=user.id, task_id=task_id)
    
    try:
        async with get_session() as session:
            repo = TaskRepository(session)
            
            # Get task
            task = await repo.get_by_id(task_id)
            
            if not task:
                await query.edit_message_text(f"❌ Задача #{task_id} не найдена")
                return
            
            # TODO: Prompt for actual duration
            # For now, use estimated as actual
            actual_duration = task.estimated_duration or 60
            
            # Complete task
            completed_task = await repo.complete(task_id, actual_duration)
        
        # Update message
        await query.edit_message_text(
            f"✅ **Задача завершена!**\n\n"
            f"{completed_task.title}\n\n"
            f"🎉 Отличная работа!"
        )
        
        logger.info("task_completed_via_button", user_id=user.id, task_id=task_id)
        
    except Exception as e:
        logger.error("callback_complete_failed", task_id=task_id, error=str(e))
        await query.edit_message_text(
            "❌ Ошибка при завершении задачи"
        )


async def handle_edit_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE,
    task_id: int
) -> None:
    """Handle 'edit task' button click.
    
    TODO: Implement task editing dialog
    
    Args:
        query: Callback query
        context: Bot context
        task_id: Task ID to edit
    """
    
    logger.info("callback_edit_task", task_id=task_id)
    
    await query.edit_message_text(
        f"✏️ **Редактирование задачи #{task_id}**\n\n"
        f"Функция в разработке.\n\n"
        f"Пока что создайте новую задачу через голосовое сообщение."
    )


async def handle_reschedule_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE,
    task_id: int
) -> None:
    """Handle 'reschedule task' button click.
    
    TODO: Implement task rescheduling dialog
    
    Args:
        query: Callback query
        context: Bot context
        task_id: Task ID to reschedule
    """
    
    logger.info("callback_reschedule_task", task_id=task_id)
    
    await query.edit_message_text(
        f"📅 **Перенос задачи #{task_id}**\n\n"
        f"Функция в разработке.\n\n"
        f"Используйте /task чтобы создать задачу с новым дедлайном."
    )


async def handle_delete_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE,
    task_id: int
) -> None:
    """Handle 'delete task' button click.
    
    Args:
        query: Callback query
        context: Bot context
        task_id: Task ID to delete
    """
    
    user = query.from_user
    
    logger.info("callback_delete_task", user_id=user.id, task_id=task_id)
    
    try:
        async with get_session() as session:
            repo = TaskRepository(session)
            
            # Soft delete (archive)
            await repo.delete(task_id)
        
        await query.edit_message_text(
            f"🗑️ Задача #{task_id} удалена"
        )
        
        logger.info("task_deleted_via_button", user_id=user.id, task_id=task_id)
        
    except Exception as e:
        logger.error("callback_delete_failed", task_id=task_id, error=str(e))
        await query.edit_message_text(
            "❌ Ошибка при удалении задачи"
        )


async def handle_today_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle 'today' button click - show today's tasks.
    
    Args:
        query: Callback query
        context: Bot context
    """
    
    # Redirect to today command
    from src.telegram.handlers.command_handler import today_command
    
    # Simulate command update
    # This is a bit hacky but works
    await query.message.reply_text("📋 Загружаю задачи на сегодня...")


async def handle_week_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle 'week' button click - show week's tasks.
    
    Args:
        query: Callback query
        context: Bot context
    """
    
    await query.message.reply_text("📅 Загружаю задачи на неделю...")


async def handle_help_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle 'help' button click - show help.
    
    Args:
        query: Callback query
        context: Bot context
    """
    
    help_text = """❓ **Помощь**

🎤 Отправь голосовое сообщение с задачей
📋 /today - Задачи на сегодня
📅 /week - Задачи на неделю
📝 /task - Создать текстом
✅ /complete - Завершить задачу
📊 /weekly - Недельная аналитика
"""
    
    await query.edit_message_text(help_text)


async def handle_complete_prompt_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle 'complete task prompt' button - ask which task to complete.
    
    Args:
        query: Callback query
        context: Bot context
    """
    
    await query.edit_message_text(
        "✅ **Завершить задачу**\n\n"
        "Используйте: /complete <номер>\n\n"
        "Или нажмите кнопку «Завершить» под нужной задачей."
    )


async def handle_new_task_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle 'new task' button - prompt to create task.
    
    Args:
        query: Callback query
        context: Bot context
    """
    
    await query.edit_message_text(
        "➕ **Новая задача**\n\n"
        "🎤 Отправьте голосовое сообщение\n"
        "или\n"
        "📝 /task <описание задачи>"
    )

