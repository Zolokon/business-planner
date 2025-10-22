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
        elif action == "edit_title":
            await handle_edit_title_callback(query, context, int(param))
        elif action == "edit_priority":
            await handle_edit_priority_callback(query, context, int(param))
        elif action == "edit_deadline":
            await handle_edit_deadline_callback(query, context, int(param))
        elif action == "edit_cancel":
            await handle_edit_cancel_callback(query, context, int(param))
        elif action == "set_priority":
            await handle_set_priority_callback(query, context, param)
        elif action == "set_deadline":
            await handle_set_deadline_callback(query, context, param)
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
        elif action == "evening_reschedule":
            await handle_evening_reschedule_callback(query, context, int(param))
        elif action == "evening_complete":
            await handle_evening_complete_callback(query, context, int(param))
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
        session_gen = get_session()
        session = await anext(session_gen)
        try:
            repo = TaskRepository(session)

            # Get task
            task = await repo.get_by_id(task_id)

            if not task:
                await query.edit_message_text(f"[ОШИБКА] Задача #{task_id} не найдена")
                return

            # TODO: Prompt for actual duration
            # For now, use estimated as actual
            actual_duration = task.estimated_duration or 60

            # Complete task
            completed_task = await repo.complete(task_id, actual_duration)
        finally:
            await session.close()

        # Update message
        await query.edit_message_text(
            f"ЗАДАЧА ЗАВЕРШЕНА\n\n"
            f"{completed_task.title}\n\n"
            f"Отличная работа!"
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

    Args:
        query: Callback query
        context: Bot context
        task_id: Task ID to edit
    """

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    logger.info("callback_edit_task", task_id=task_id)

    # Get task details
    try:
        session_gen = get_session()
        session = await anext(session_gen)
        try:
            repo = TaskRepository(session)
            task = await repo.get_by_id(task_id)

            if not task:
                await query.edit_message_text(f"[ОШИБКА] Задача #{task_id} не найдена")
                return
        finally:
            await session.close()

        # Show edit menu - clean formatting
        business_names = {1: "Inventum", 2: "Inventum Lab", 3: "R&D", 4: "Trade"}
        priority_names = {1: "ВЫСОКИЙ", 2: "СРЕДНИЙ", 3: "НИЗКИЙ", 4: "ОТЛОЖЕННЫЙ"}

        business_name = business_names.get(task.business_id, f"Business {task.business_id}")
        priority_name = priority_names.get(task.priority, "Не указан")
        deadline_text = task.deadline.strftime("%d.%m.%Y") if task.deadline else "Не установлен"

        message = f"""РЕДАКТИРОВАНИЕ ЗАДАЧИ #{task_id}

{task.title}

Бизнес:    {business_name}
Приоритет: {priority_name}
Дедлайн:   {deadline_text}

Что хотите изменить?"""

        keyboard = [
            [
                InlineKeyboardButton("Название", callback_data=f"edit_title:{task_id}"),
                InlineKeyboardButton("Приоритет", callback_data=f"edit_priority:{task_id}")
            ],
            [
                InlineKeyboardButton("Дедлайн", callback_data=f"edit_deadline:{task_id}"),
                InlineKeyboardButton("Отмена", callback_data=f"edit_cancel:{task_id}")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)

    except Exception as e:
        logger.error("callback_edit_failed", task_id=task_id, error=str(e))
        await query.edit_message_text("[ОШИБКА] Ошибка при загрузке задачи")


async def handle_edit_title_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE,
    task_id: int
) -> None:
    """Handle edit title button - prompt for new title.

    Args:
        query: Callback query
        context: Bot context
        task_id: Task ID
    """

    # Store task_id in user context for next message
    context.user_data["editing_task_id"] = task_id
    context.user_data["editing_field"] = "title"

    await query.edit_message_text(
        f"✏️ **Изменение названия задачи #{task_id}**\n\n"
        f"Отправьте новое название задачи текстовым сообщением."
    )


async def handle_edit_priority_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE,
    task_id: int
) -> None:
    """Handle edit priority button - show priority options.

    Args:
        query: Callback query
        context: Bot context
        task_id: Task ID
    """

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = [
        [InlineKeyboardButton("🔴 Высокий", callback_data=f"set_priority:1:{task_id}")],
        [InlineKeyboardButton("🟡 Средний", callback_data=f"set_priority:2:{task_id}")],
        [InlineKeyboardButton("🟢 Низкий", callback_data=f"set_priority:3:{task_id}")],
        [InlineKeyboardButton("⚪ Нет срочности", callback_data=f"set_priority:4:{task_id}")],
        [InlineKeyboardButton("❌ Отмена", callback_data=f"edit:{task_id}")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"🎯 **Выберите приоритет для задачи #{task_id}:**",
        reply_markup=reply_markup
    )


async def handle_edit_deadline_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE,
    task_id: int
) -> None:
    """Handle edit deadline button - show deadline options.

    Args:
        query: Callback query
        context: Bot context
        task_id: Task ID
    """

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    from datetime import datetime, timedelta

    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    in_3_days = today + timedelta(days=3)
    in_week = today + timedelta(days=7)

    keyboard = [
        [InlineKeyboardButton("📅 Сегодня", callback_data=f"set_deadline:{today.isoformat()}:{task_id}")],
        [InlineKeyboardButton("📅 Завтра", callback_data=f"set_deadline:{tomorrow.isoformat()}:{task_id}")],
        [InlineKeyboardButton("📅 Через 3 дня", callback_data=f"set_deadline:{in_3_days.isoformat()}:{task_id}")],
        [InlineKeyboardButton("📅 Через неделю", callback_data=f"set_deadline:{in_week.isoformat()}:{task_id}")],
        [InlineKeyboardButton("❌ Отмена", callback_data=f"edit:{task_id}")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"📅 **Выберите дедлайн для задачи #{task_id}:**",
        reply_markup=reply_markup
    )


async def handle_edit_cancel_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE,
    task_id: int
) -> None:
    """Handle edit cancel button.

    Args:
        query: Callback query
        context: Bot context
        task_id: Task ID
    """

    # Clear editing context
    context.user_data.pop("editing_task_id", None)
    context.user_data.pop("editing_field", None)

    await query.edit_message_text("✅ Редактирование отменено")


async def handle_set_priority_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE,
    param: str
) -> None:
    """Handle set priority button - update task priority.

    Args:
        query: Callback query
        context: Bot context
        param: "priority:task_id" string
    """

    from src.domain.models import TaskUpdate

    # Parse param: "priority:task_id"
    parts = param.split(":")
    if len(parts) != 2:
        await query.edit_message_text("[ОШИБКА] Ошибка формата данных")
        return

    priority = int(parts[0])
    task_id = int(parts[1])

    try:
        session_gen = get_session()
        session = await anext(session_gen)
        try:
            repo = TaskRepository(session)

            # Update priority
            task_update = TaskUpdate(priority=priority)
            updated_task = await repo.update(task_id, task_update)
        finally:
            await session.close()

        priority_names = {1: "ВЫСОКИЙ", 2: "СРЕДНИЙ", 3: "НИЗКИЙ", 4: "ОТЛОЖЕННЫЙ"}
        priority_name = priority_names.get(priority, "Неизвестно")

        await query.edit_message_text(
            f"ПРИОРИТЕТ ОБНОВЛЕН\n\n"
            f"Задача: {updated_task.title}\n"
            f"Новый приоритет: {priority_name}"
        )

        logger.info("task_priority_updated", task_id=task_id, priority=priority)

    except Exception as e:
        logger.error("callback_set_priority_failed", task_id=task_id, error=str(e))
        await query.edit_message_text("❌ Ошибка при обновлении приоритета")


async def handle_set_deadline_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE,
    param: str
) -> None:
    """Handle set deadline button - update task deadline.

    Args:
        query: Callback query
        context: Bot context
        param: "date:task_id" string
    """

    from src.domain.models import TaskUpdate
    from datetime import datetime

    # Parse param: "date:task_id"
    parts = param.split(":")
    if len(parts) != 2:
        await query.edit_message_text("[ОШИБКА] Ошибка формата данных")
        return

    date_str = parts[0]
    task_id = int(parts[1])

    try:
        # Parse date (will be midnight 00:00 by default if no time specified)
        deadline_date = datetime.fromisoformat(date_str)
        # Keep as-is: 00:00 for date-only deadlines
        deadline = deadline_date

        session_gen = get_session()
        session = await anext(session_gen)
        try:
            repo = TaskRepository(session)

            # Update deadline
            task_update = TaskUpdate(deadline=deadline)
            updated_task = await repo.update(task_id, task_update)
        finally:
            await session.close()

        deadline_text = deadline.strftime("%d.%m.%Y")

        await query.edit_message_text(
            f"ДЕДЛАЙН ОБНОВЛЕН\n\n"
            f"Задача: {updated_task.title}\n"
            f"Новый дедлайн: {deadline_text}"
        )

        logger.info("task_deadline_updated", task_id=task_id, deadline=deadline_text)

    except Exception as e:
        logger.error("callback_set_deadline_failed", task_id=task_id, error=str(e))
        await query.edit_message_text("❌ Ошибка при обновлении дедлайна")


async def handle_reschedule_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE,
    task_id: int
) -> None:
    """Handle 'reschedule task' button click - redirect to edit deadline.

    Args:
        query: Callback query
        context: Bot context
        task_id: Task ID to reschedule
    """

    logger.info("callback_reschedule_task", task_id=task_id)

    # Redirect to deadline editing
    await handle_edit_deadline_callback(query, context, task_id)


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
        session_gen = get_session()
        session = await anext(session_gen)
        try:
            repo = TaskRepository(session)

            # Soft delete (archive)
            await repo.delete(task_id)
        finally:
            await session.close()

        await query.edit_message_text(
            f"ЗАДАЧА #{task_id} УДАЛЕНА"
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


async def handle_evening_reschedule_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE,
    task_id: int
) -> None:
    """Handle 'reschedule to tomorrow' button from evening summary.

    Args:
        query: Callback query
        context: Bot context
        task_id: Task ID to reschedule
    """
    from src.domain.models import TaskUpdate
    from datetime import datetime, timedelta

    user = query.from_user

    logger.info("evening_reschedule_task", user_id=user.id, task_id=task_id)

    try:
        session_gen = get_session()
        session = await anext(session_gen)
        try:
            repo = TaskRepository(session)

            # Get current task
            task = await repo.get_by_id(task_id)
            if not task:
                await query.edit_message_text(f"❌ Задача #{task_id} не найдена")
                return

            # Calculate tomorrow's date
            tomorrow = datetime.now().date() + timedelta(days=1)

            # Keep time if exists, otherwise set to 00:00
            if task.deadline and (task.deadline.hour != 0 or task.deadline.minute != 0):
                # Has specific time, keep it
                new_deadline = datetime.combine(tomorrow, task.deadline.time())
            else:
                # No specific time, set to midnight (00:00)
                new_deadline = datetime.combine(tomorrow, datetime.min.time())

            # Update deadline
            task_update = TaskUpdate(deadline=new_deadline)
            updated_task = await repo.update(task_id, task_update)

        finally:
            await session.close()

        # Format response
        deadline_str = new_deadline.strftime("%d.%m.%Y")
        if new_deadline.hour != 0 or new_deadline.minute != 0:
            deadline_str += f" в {new_deadline.strftime('%H:%M')}"

        await query.edit_message_text(
            f"✅ ЗАДАЧА ПЕРЕНЕСЕНА НА ЗАВТРА\n\n"
            f"{updated_task.title}\n\n"
            f"Новый дедлайн: {deadline_str}"
        )

        logger.info("evening_task_rescheduled", task_id=task_id, new_deadline=deadline_str)

    except Exception as e:
        logger.error("evening_reschedule_failed", task_id=task_id, error=str(e))
        await query.edit_message_text("❌ Ошибка при переносе задачи")


async def handle_evening_complete_callback(
    query,
    context: ContextTypes.DEFAULT_TYPE,
    task_id: int
) -> None:
    """Handle 'complete task' button from evening summary.

    Args:
        query: Callback query
        context: Bot context
        task_id: Task ID to complete
    """
    user = query.from_user

    logger.info("evening_complete_task", user_id=user.id, task_id=task_id)

    try:
        session_gen = get_session()
        session = await anext(session_gen)
        try:
            repo = TaskRepository(session)

            # Get task
            task = await repo.get_by_id(task_id)
            if not task:
                await query.edit_message_text(f"❌ Задача #{task_id} не найдена")
                return

            # Use estimated duration as actual (user can adjust later if needed)
            actual_duration = task.estimated_duration or 60

            # Complete task
            completed_task = await repo.complete(task_id, actual_duration)

        finally:
            await session.close()

        await query.edit_message_text(
            f"✅ ЗАДАЧА ЗАВЕРШЕНА\n\n"
            f"{completed_task.title}\n\n"
            f"Отличная работа!"
        )

        logger.info("evening_task_completed", user_id=user.id, task_id=task_id)

    except Exception as e:
        logger.error("evening_complete_failed", task_id=task_id, error=str(e))
        await query.edit_message_text("❌ Ошибка при завершении задачи")

