"""
Command Handlers - Business Planner.

Implements Telegram bot commands:
/start, /today, /week, /task, /complete, /weekly, /help

Reference: docs/03-api/telegram-commands.md
"""

from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import select

from src.utils.logger import logger
from src.infrastructure.database import get_session
from src.infrastructure.database.models import UserORM
from src.infrastructure.database.repositories.task_repository import TaskRepository
from src.domain.models.enums import TaskStatus


# ============================================================================
# /start - Welcome & Onboarding
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command - welcome message.
    
    Shows:
    - Welcome message
    - How to use the bot
    - Quick start guide
    
    Reference: docs/03-api/telegram-commands.md (/start)
    """
    
    user = update.effective_user
    
    logger.info("command_start", user_id=user.id, username=user.username)
    
    welcome_message = f"""👋 Привет, {user.first_name}!

Я **Business Planner** - твой голосовой помощник для управления задачами.

🎤 **Как использовать:**
• Отправь голосовое сообщение с описанием задачи
• Я распознаю речь, определю бизнес, дедлайн и исполнителя
• Задача будет создана автоматически

📋 **Команды:**
/today - Задачи на сегодня
/week - Задачи на неделю
/task - Создать задачу текстом
/complete - Завершить задачу
/weekly - Недельная аналитика (пятница)
/help - Помощь

🚀 **Попробуй прямо сейчас:**
Отправь голосовое сообщение с задачей!

Например: "Нужно починить фрезер для Иванова до завтра"
"""
    
    # Quick action buttons
    keyboard = [
        [
            InlineKeyboardButton("📋 Задачи на сегодня", callback_data="today"),
            InlineKeyboardButton("📅 На неделю", callback_data="week")
        ],
        [
            InlineKeyboardButton("❓ Помощь", callback_data="help")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)


# ============================================================================
# /today - Today's Tasks
# ============================================================================

async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /today command - show tasks for today.
    
    Groups tasks by:
    - Priority (1 = DO NOW, 2 = Important, 3 = Normal, 4 = Backlog)
    - Business
    
    Reference: docs/03-api/telegram-commands.md (/today)
    """
    
    user = update.effective_user
    
    logger.info("command_today", user_id=user.id)

    await update.message.reply_chat_action("typing")

    try:
        # Get database session
        session_gen = get_session()
        session = await anext(session_gen)
        try:
            # Map Telegram user to DB user
            stmt = select(UserORM).where(UserORM.telegram_id == user.id)
            result_db = await session.execute(stmt)
            db_user = result_db.scalar_one_or_none()

            if not db_user:
                await update.message.reply_text(
                    "❌ Пользователь не найден в базе данных.\n"
                    "Пожалуйста, отправьте команду /start для регистрации."
                )
                return

            db_user_id = db_user.id

            repo = TaskRepository(session)

            # Get today's tasks (deadline = today)
            today = datetime.now().date()
            tasks = await repo.find_by_deadline(
                user_id=db_user_id,
                date=today
            )
        finally:
            await session.close()

        if not tasks:
            await update.message.reply_text(
                "На сегодня задач нет.\n\n"
                "Отправьте голосовое сообщение, чтобы создать задачу."
            )
            return

        # Group by priority
        priority_names = {1: "ВЫСОКИЙ", 2: "СРЕДНИЙ", 3: "НИЗКИЙ", 4: "ОТЛОЖЕННЫЙ"}
        business_names = {1: "Inventum", 2: "Inventum Lab", 3: "R&D", 4: "Trade"}

        tasks_by_priority = {}
        for task in tasks:
            if task.priority not in tasks_by_priority:
                tasks_by_priority[task.priority] = []
            tasks_by_priority[task.priority].append(task)

        # Format message - clean, structured
        message = f"ЗАДАЧИ НА СЕГОДНЯ ({len(tasks)})\n"
        message += "=" * 40 + "\n\n"

        for priority in sorted(tasks_by_priority.keys()):
            priority_tasks = tasks_by_priority[priority]
            message += f"[{priority_names[priority]}] ({len(priority_tasks)})\n"
            message += "-" * 40 + "\n"

            for task in priority_tasks[:5]:  # Max 5 per priority
                business_name = business_names.get(task.business_id, f"Business {task.business_id}")

                message += f"\n{task.title}\n"
                message += f"  Бизнес: {business_name}"

                if task.estimated_duration:
                    hours = task.estimated_duration // 60
                    mins = task.estimated_duration % 60
                    time_str = f"{hours}ч {mins}м" if hours > 0 else f"{mins}м"
                    message += f" | Время: ~{time_str}"

                if task.assigned_to:
                    message += f" | ID: {task.assigned_to}"

                message += "\n"

            message += "\n"
        
        # Add action buttons
        keyboard = [
            [
                InlineKeyboardButton("Завершить задачу", callback_data="complete_prompt"),
                InlineKeyboardButton("Новая задача", callback_data="new_task")
            ],
            [
                InlineKeyboardButton("На неделю", callback_data="week")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error("command_today_failed", user_id=user.id, error=str(e))
        await update.message.reply_text(
            "❌ Ошибка при загрузке задач. Попробуйте позже."
        )


# ============================================================================
# /week - Week's Tasks
# ============================================================================

async def week_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /week command - show tasks for the week.
    
    Reference: docs/03-api/telegram-commands.md (/week)
    """
    
    user = update.effective_user
    
    logger.info("command_week", user_id=user.id)

    await update.message.reply_chat_action("typing")

    try:
        # Get database session
        session_gen = get_session()
        session = await anext(session_gen)
        try:
            # Map Telegram user to DB user
            stmt = select(UserORM).where(UserORM.telegram_id == user.id)
            result_db = await session.execute(stmt)
            db_user = result_db.scalar_one_or_none()

            if not db_user:
                await update.message.reply_text(
                    "❌ Пользователь не найден в базе данных.\n"
                    "Пожалуйста, отправьте команду /start для регистрации."
                )
                return

            db_user_id = db_user.id

            repo = TaskRepository(session)

            # Get this week's tasks
            today = datetime.now().date()
            week_end = today + timedelta(days=7)

            tasks = await repo.find_by_date_range(
                user_id=db_user_id,
                start_date=today,
                end_date=week_end
            )
        finally:
            await session.close()

        if not tasks:
            await update.message.reply_text(
                "✅ На эту неделю задач нет!\n\n"
                "Отправь голосовое сообщение, чтобы создать задачу."
            )
            return
        
        # Group by day
        tasks_by_day = {}
        for task in tasks:
            if task.deadline:
                day_key = task.deadline.date()
                if day_key not in tasks_by_day:
                    tasks_by_day[day_key] = []
                tasks_by_day[day_key].append(task)
        
        # Format message
        weekday_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        business_emoji = {1: "🔧", 2: "🦷", 3: "🔬", 4: "💼"}
        
        message = f"📅 **Задачи на неделю** ({len(tasks)} шт.)\n\n"
        
        for day in sorted(tasks_by_day.keys()):
            day_tasks = tasks_by_day[day]
            weekday = weekday_names[day.weekday()]
            
            # Highlight today
            if day == today:
                message += f"**🔹 {weekday}, {day.strftime('%d.%m')} (СЕГОДНЯ)**\n"
            else:
                message += f"**{weekday}, {day.strftime('%d.%m')}**\n"
            
            for task in day_tasks[:3]:  # Max 3 per day
                biz_emoji = business_emoji.get(task.business_id, "📋")
                message += f"  {biz_emoji} {task.title[:40]}{'...' if len(task.title) > 40 else ''}\n"
            
            if len(day_tasks) > 3:
                message += f"  ... и еще {len(day_tasks) - 3}\n"
            
            message += "\n"
        
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error("command_week_failed", user_id=user.id, error=str(e))
        await update.message.reply_text(
            "❌ Ошибка при загрузке задач. Попробуйте позже."
        )


# ============================================================================
# /task - Create Task (Text)
# ============================================================================

async def task_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /task command - create task from text.
    
    Usage: /task <описание задачи>
    
    Reference: docs/03-api/telegram-commands.md (/task)
    """
    
    user = update.effective_user
    
    logger.info("command_task", user_id=user.id)
    
    # Get task text from command arguments
    if not context.args:
        await update.message.reply_text(
            "📝 **Создание задачи текстом**\n\n"
            "Использование: /task <описание>\n\n"
            "Пример:\n"
            "/task Починить фрезер для Иванова до завтра\n\n"
            "💡 Подсказка: проще отправить голосовое сообщение!"
        )
        return
    
    task_text = " ".join(context.args)
    
    await update.message.reply_chat_action("typing")
    
    try:
        # Use task parser (same as voice)
        from src.ai.parsers.task_parser import parse_task_from_transcript
        from src.infrastructure.database.repositories.task_repository import TaskRepository
        
        # Get database session and map user
        session_gen = get_session()
        session = await anext(session_gen)
        try:
            # Map Telegram user to DB user
            stmt = select(UserORM).where(UserORM.telegram_id == user.id)
            result_db = await session.execute(stmt)
            db_user = result_db.scalar_one_or_none()

            if not db_user:
                await update.message.reply_text(
                    "❌ Пользователь не найден в базе данных.\n"
                    "Пожалуйста, отправьте команду /start для регистрации."
                )
                return

            db_user_id = db_user.id

            # Parse text
            parsed = await parse_task_from_transcript(
                transcript=task_text,
                user_id=db_user_id
            )

            # Create task
            repo = TaskRepository(session)
            task = await repo.create(parsed, user_id=db_user_id)
        finally:
            await session.close()
        
        # Format response
        business_emoji = {1: "🔧", 2: "🦷", 3: "🔬", 4: "💼"}
        business_names = {1: "Inventum", 2: "Inventum Lab", 3: "R&D", 4: "Trade"}

        business_name = business_names.get(task.business_id, f"Business {task.business_id}")

        response = f"""✅ Задача создана!

{task.title}

{business_emoji.get(task.business_id, '📋')} Бизнес: {business_name}
"""
        
        if task.deadline:
            response += f"📅 Дедлайн: {task.deadline.strftime('%d.%m.%Y %H:%M')}\n"
        
        if task.estimated_duration:
            hours = task.estimated_duration // 60
            mins = task.estimated_duration % 60
            time_str = f"{hours}ч {mins}м" if hours > 0 else f"{mins}м"
            response += f"⏱️ ~{time_str}\n"
        
        # Add action buttons
        keyboard = [
            [
                InlineKeyboardButton("✅ Завершить", callback_data=f"complete:{task.id}"),
                InlineKeyboardButton("✏️ Изменить", callback_data=f"edit:{task.id}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, reply_markup=reply_markup)
        
        logger.info("task_created_via_text", user_id=user.id, task_id=task.id)
        
    except Exception as e:
        logger.error("command_task_failed", user_id=user.id, error=str(e))
        await update.message.reply_text(
            "❌ Не удалось создать задачу. Попробуйте еще раз."
        )


# ============================================================================
# /complete - Complete Task
# ============================================================================

async def complete_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /complete command - mark task as completed.
    
    Usage: /complete <task_id>
    
    Reference: docs/03-api/telegram-commands.md (/complete)
    """
    
    user = update.effective_user
    
    logger.info("command_complete", user_id=user.id)
    
    # Check if task_id provided
    if not context.args:
        # Show list of open tasks to complete
        await update.message.reply_text(
            "✅ **Завершение задачи**\n\n"
            "Использование: /complete <номер задачи>\n\n"
            "Или используйте кнопку «Завершить» под задачей."
        )
        return
    
    try:
        task_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Неверный номер задачи")
        return
    
    await update.message.reply_chat_action("typing")

    try:
        # Get database session
        session_gen = get_session()
        session = await anext(session_gen)
        try:
            repo = TaskRepository(session)

            # Get task
            task = await repo.get_by_id(task_id)

            if not task:
                await update.message.reply_text(f"❌ Задача #{task_id} не найдена")
                return

            # TODO: Check if user owns this task

            # Complete task (prompt for actual duration)
            # For now, use estimated duration as actual
            actual_duration = task.estimated_duration or 60

            completed_task = await repo.complete(task_id, actual_duration)
        finally:
            await session.close()
        
        await update.message.reply_text(
            f"✅ Задача завершена!\n\n"
            f"**{completed_task.title}**\n\n"
            f"🎉 Отличная работа!"
        )
        
        logger.info("task_completed_via_command", user_id=user.id, task_id=task_id)
        
    except Exception as e:
        logger.error("command_complete_failed", user_id=user.id, error=str(e))
        await update.message.reply_text(
            "❌ Ошибка при завершении задачи. Попробуйте позже."
        )


# ============================================================================
# /weekly - Weekly Analytics
# ============================================================================

async def weekly_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /weekly command - generate weekly analytics.
    
    Uses GPT-5 for deep insights (Tier 3).
    
    Reference:
    - docs/03-api/telegram-commands.md (/weekly)
    - docs/05-ai-specifications/prompts/weekly-analytics.md
    """
    
    user = update.effective_user
    
    logger.info("command_weekly", user_id=user.id)
    
    await update.message.reply_text(
        "📊 Генерирую недельную аналитику...\n"
        "Это займет ~30 секунд."
    )
    
    await update.message.reply_chat_action("typing")
    
    try:
        # TODO: Implement weekly analytics with GPT-5
        # This is a placeholder
        
        analytics = """📊 **Недельная аналитика** (16-22 окт)

✅ **Выполнено**: 23 задачи
⏱️ **Время**: 47 часов
🎯 **Точность оценки**: 83% (отлично!)

**🏆 Топ достижения:**
1. 🔧 Inventum - 12 задач (фрезеры)
2. 🦷 Lab - 8 задач (коронки)
3. 🔬 R&D - 3 прототипа

**⚠️ Проблемные места:**
• Задачи по Китаю часто переносятся
• Недооценка времени на диагностику

**💡 Рекомендации на следующую неделю:**
• Закладывать +20% времени на диагностику
• Договориться с Славой о регулярных созвонах по Import&Trade
• Делегировать больше задач Максиму и Диме
"""
        
        await update.message.reply_text(analytics)
        
        logger.info("weekly_analytics_generated", user_id=user.id)
        
    except Exception as e:
        logger.error("command_weekly_failed", user_id=user.id, error=str(e))
        await update.message.reply_text(
            "❌ Ошибка при генерации аналитики. Попробуйте позже."
        )


# ============================================================================
# /help - Help
# ============================================================================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command - show help message.
    
    Reference: docs/03-api/telegram-commands.md (/help)
    """
    
    user = update.effective_user
    
    logger.info("command_help", user_id=user.id)
    
    help_text = """❓ **Помощь - Business Planner**

🎤 **Голосовые сообщения** (основной способ)
Отправь голосовое сообщение с описанием задачи:
• "Нужно починить фрезер для Иванова до завтра"
• "Максиму сделать прототип крышки к понедельнику"
• "Позвонить поставщику в Китае сегодня вечером"

Я автоматически определю:
✓ Бизнес (Inventum, Lab, R&D, Trade)
✓ Исполнителя (8 членов команды)
✓ Дедлайн (с учетом рабочих дней)
✓ Приоритет (1-4)
✓ Время выполнения (на основе истории)

📋 **Команды:**
/today - Задачи на сегодня
/week - Задачи на неделю
/task <текст> - Создать задачу текстом
/complete <ID> - Завершить задачу
/weekly - Недельная аналитика (пятница)
/help - Эта справка

💡 **Советы:**
• Говорите естественно, как обычно
• Указывайте имя исполнителя для делегирования
• Уточняйте дедлайны ("завтра", "к понедельнику")
• Используйте кнопки под задачами для быстрых действий

🚀 **Попробуй сейчас:**
Отправь голосовое сообщение!
"""
    
    await update.message.reply_text(help_text)

