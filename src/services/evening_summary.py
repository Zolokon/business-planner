"""
Evening Summary Service - Business Planner.

Sends evening task summary to user every day at 19:00.
Shows incomplete tasks with quick action buttons.

Features:
- Shows tasks with deadline today (not completed)
- Shows overdue tasks (deadline passed)
- Grouped by business
- Interactive buttons: Reschedule to tomorrow / Complete
- Celebration message if all done

Reference:
- User requirement: "в конце дня хочу увидеть задачи которые не выполнились"
"""

from datetime import datetime, date, timedelta
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from src.domain.models import Task
from src.domain.constants import BUSINESS_NAMES, PRIORITY_CIRCLES
from src.infrastructure.database.repositories.task_repository import TaskRepository
from src.utils.logger import logger


# ============================================================================
# Helper Functions
# ============================================================================

def format_task_deadline(task: Task) -> str:
    """Format deadline for evening summary.

    Args:
        task: Task with deadline

    Returns:
        Formatted deadline string

    Examples:
        today with time → "сегодня, 15:00"
        today no time → "сегодня"
        overdue → "просрочено (21.10)"
    """
    if not task.deadline:
        return "без дедлайна"

    today = date.today()
    task_date = task.deadline.date()

    # Check if overdue
    if task_date < today:
        return f"просрочено ({task.deadline.strftime('%d.%m')})"

    # Today
    if task_date == today:
        if task.deadline.hour != 0 or task.deadline.minute != 0:
            return f"сегодня, {task.deadline.strftime('%H:%M')}"
        else:
            return "сегодня"

    # Future (shouldn't happen in evening summary, but handle it)
    return task.deadline.strftime("%d.%m")


def format_task_card(task: Task) -> str:
    """Format single task card for evening summary.

    Args:
        task: Task to format

    Returns:
        Formatted task card with details

    Example:
        🔴 Починить фрезер для Иванова
        Дедлайн: сегодня, 15:00
    """
    # Priority circle
    circle = PRIORITY_CIRCLES.get(task.priority, "🟡")

    # Task title with executor
    title = f"{circle} {task.title}"
    if task.assigned_to:
        title += f" ({task.assigned_to})"

    # Deadline
    deadline_text = format_task_deadline(task)

    return f"{title}\nДедлайн: {deadline_text}"


def create_task_buttons(task_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard with action buttons for task.

    Args:
        task_id: Task ID

    Returns:
        InlineKeyboardMarkup with Reschedule and Complete buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("↪️ На завтра", callback_data=f"evening_reschedule:{task_id}"),
            InlineKeyboardButton("✅ Готово", callback_data=f"evening_complete:{task_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def sort_tasks_key(task: Task) -> tuple:
    """Sort key for evening summary: overdue first, then by priority.

    Args:
        task: Task to sort

    Returns:
        Sort key tuple (is_overdue, priority, deadline)
    """
    today = date.today()

    # Check if overdue
    is_overdue = False
    if task.deadline:
        is_overdue = task.deadline.date() < today

    # Overdue tasks first (0), then today's tasks (1)
    overdue_priority = 0 if is_overdue else 1

    # Deadline timestamp (overdue first, then by time)
    deadline_ts = task.deadline.timestamp() if task.deadline else float('inf')

    return (overdue_priority, task.priority, deadline_ts)


# ============================================================================
# Main Service Function
# ============================================================================

async def generate_evening_summary(
    session: AsyncSession,
    user_id: int
) -> tuple[str, List[tuple[str, InlineKeyboardMarkup]] | None]:
    """Generate evening task summary for user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        Tuple of (header_message, list of (task_message, keyboard) tuples)
        If all tasks done: (success_message, None)

    Logic:
    - Fetch tasks with status "open" or "in_progress"
    - Filter: deadline today or overdue
    - Exclude backlog (priority 4)
    - Group by business
    - Sort: overdue first, then by priority
    """
    repo = TaskRepository(session)

    # Get today's date
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Fetch incomplete tasks for all businesses
    incomplete_tasks_by_business: Dict[int, List[Task]] = {}

    for business_id in [1, 2, 3, 4]:
        # Get only open tasks (not completed/archived)
        tasks = await repo.find_by_business(
            user_id=user_id,
            business_id=business_id,
            status="open",  # Only open tasks
            limit=100
        )

        # Filter: all open tasks except backlog (so user can complete any task)
        incomplete_tasks = [
            task for task in tasks
            if task.priority != 4  # Not backlog
        ]

        if incomplete_tasks:
            # Sort: overdue first, then by priority
            incomplete_tasks.sort(key=sort_tasks_key)
            incomplete_tasks_by_business[business_id] = incomplete_tasks

    # Check if all done
    if not incomplete_tasks_by_business:
        success_message = (
            "🎉 ОТЛИЧНАЯ РАБОТА!\n\n"
            "Все задачи на сегодня выполнены.\n"
            "Хорошего вечера!"
        )
        logger.info("evening_summary_all_done", user_id=user_id)
        return (success_message, None)

    # Build header
    today_formatted = today.strftime("%d.%m.%Y")
    total_tasks = sum(len(tasks) for tasks in incomplete_tasks_by_business.values())

    header = (
        f"📊 ИТОГИ ДНЯ ({today_formatted})\n\n"
        f"Незавершённые задачи: {total_tasks}\n"
    )

    # Build task messages with buttons
    task_messages = []

    for business_id, tasks in incomplete_tasks_by_business.items():
        business_name = BUSINESS_NAMES[business_id]

        # Add business header to first task of business
        for i, task in enumerate(tasks):
            # Format task card
            task_card = format_task_card(task)

            # Add business name as prefix for first task
            if i == 0:
                task_message = f"\n{business_name}\n\n{task_card}"
            else:
                task_message = f"\n{task_card}"

            # Create buttons
            keyboard = create_task_buttons(task.id)

            task_messages.append((task_message, keyboard))

    logger.info(
        "evening_summary_generated",
        user_id=user_id,
        incomplete_tasks=total_tasks,
        businesses=len(incomplete_tasks_by_business)
    )

    return (header, task_messages)


async def send_evening_summary_to_user(
    bot: Bot,
    user_telegram_id: int,
    session: AsyncSession,
    user_id: int
) -> None:
    """Send evening summary to user via Telegram.

    Args:
        bot: Telegram Bot instance
        user_telegram_id: User's Telegram chat ID
        session: Database session
        user_id: User ID in database

    Raises:
        Exception if sending fails
    """
    try:
        # Generate summary
        header, task_messages = await generate_evening_summary(session, user_id)

        # Send header
        await bot.send_message(
            chat_id=user_telegram_id,
            text=header,
            parse_mode=None
        )

        # Send individual task cards with buttons
        if task_messages:
            for task_message, keyboard in task_messages:
                await bot.send_message(
                    chat_id=user_telegram_id,
                    text=task_message,
                    reply_markup=keyboard,
                    parse_mode=None
                )

        logger.info(
            "evening_summary_sent",
            user_id=user_id,
            telegram_id=user_telegram_id,
            tasks_count=len(task_messages) if task_messages else 0
        )

    except Exception as e:
        logger.error(
            "evening_summary_send_failed",
            user_id=user_id,
            telegram_id=user_telegram_id,
            error=str(e)
        )
        raise
