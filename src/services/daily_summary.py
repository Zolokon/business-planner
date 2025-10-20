"""
Daily Summary Service - Business Planner.

Sends daily task summary to user every morning at 8 AM.

Features:
- Groups tasks by business
- Shows only relevant tasks (today/tomorrow, excluding backlog)
- Color-coded priorities (🔴🟡🟢)
- Sorted by deadline time then priority
- Shows executor if assigned

Reference:
- User requirement: "в 8 утра мне должно приходить сообщение со списком задач"
"""

from datetime import datetime, date, timedelta
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Bot

from src.domain.models import Task
from src.infrastructure.database.repositories.task_repository import TaskRepository
from src.utils.logger import logger


# ============================================================================
# Constants
# ============================================================================

BUSINESS_NAMES = {
    1: "МАСТЕРСКАЯ INVENTUM",
    2: "ЛАБОРАТОРИЯ INVENTUM LAB",
    3: "R&D",
    4: "TRADE"
}

PRIORITY_CIRCLES = {
    1: "🔴",  # Высокий - Red
    2: "🟡",  # Средний - Yellow
    3: "🟢",  # Низкий - Green
    4: "⚪"   # Отложенный - White (not shown in daily summary)
}


# ============================================================================
# Helper Functions
# ============================================================================

def format_deadline_time(task: Task) -> str:
    """Format deadline time for task display.

    Args:
        task: Task with deadline

    Returns:
        Formatted time string or empty

    Examples:
        deadline at 10:00 → "10:00"
        deadline at 00:00 (no time) → ""
        deadline tomorrow → "завтра"
    """
    if not task.deadline:
        return ""

    # Check if it's today or tomorrow
    today = date.today()
    task_date = task.deadline.date()

    # If deadline has time component (not midnight)
    if task.deadline.hour != 0 or task.deadline.minute != 0:
        time_str = task.deadline.strftime("%H:%M")

        if task_date == today:
            return time_str
        elif task_date == today + timedelta(days=1):
            return f"завтра, {time_str}"
        else:
            return f"{task.deadline.strftime('%d.%m')}, {time_str}"
    else:
        # No time specified
        if task_date == today:
            return ""
        elif task_date == today + timedelta(days=1):
            return "завтра"
        else:
            return task.deadline.strftime("%d.%m")


def format_task_line(task: Task) -> str:
    """Format single task line for daily summary.

    Args:
        task: Task to format

    Returns:
        Formatted task line

    Example:
        "🔴 Починить фрезер (Максим, 10:00)"
        "🟡 Диагностика оборудования"
        "🔴 Смоделировать коронку (Мария, завтра)"
    """
    # Priority circle
    circle = PRIORITY_CIRCLES.get(task.priority, "🟡")

    # Task title
    line = f"{circle} {task.title}"

    # Add executor and/or deadline in parentheses
    details = []

    if task.assigned_to:
        details.append(task.assigned_to)

    deadline_text = format_deadline_time(task)
    if deadline_text:
        details.append(deadline_text)

    if details:
        line += f" ({', '.join(details)})"

    return line


def sort_tasks_key(task: Task) -> tuple:
    """Sort key for tasks: by deadline time, then priority.

    Args:
        task: Task to sort

    Returns:
        Sort key tuple (deadline_timestamp, priority)

    Priority:
    1. Tasks with deadline today come first
    2. Within same day, sort by time
    3. Then by priority (High > Medium > Low)
    """
    # No deadline → sort to end
    if not task.deadline:
        return (float('inf'), task.priority)

    # Deadline timestamp for sorting
    deadline_ts = task.deadline.timestamp()

    return (deadline_ts, task.priority)


# ============================================================================
# Main Service Function
# ============================================================================

async def generate_daily_summary(
    session: AsyncSession,
    user_id: int
) -> str:
    """Generate daily task summary for user.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        Formatted summary message

    Logic:
    - Fetch all active tasks (status != 'completed')
    - Filter: deadline today or tomorrow, priority != 4 (backlog)
    - Group by business
    - Sort within business: by deadline time, then priority
    - Format message
    """
    repo = TaskRepository(session)

    # Get today and tomorrow date range
    today = date.today()
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)

    # Fetch tasks for all 4 businesses
    tasks_by_business: Dict[int, List[Task]] = {}

    for business_id in [1, 2, 3, 4]:
        # Get open/in_progress tasks for this business (exclude completed)
        tasks = await repo.find_by_business(
            user_id=user_id,
            business_id=business_id,
            status=None,  # Get all statuses, then filter
            limit=100
        )

        # Filter out completed tasks
        tasks = [t for t in tasks if t.status != "completed"]

        # Filter: relevant tasks only (today/tomorrow, not backlog)
        relevant_tasks = [
            task for task in tasks
            if task.priority != 4  # Exclude backlog
            and (
                task.deadline is None  # Include tasks without deadline
                or task.deadline.date() <= tomorrow  # Or deadline today/tomorrow
            )
        ]

        if relevant_tasks:
            # Sort by deadline time, then priority
            relevant_tasks.sort(key=sort_tasks_key)
            tasks_by_business[business_id] = relevant_tasks

    # Format message
    if not tasks_by_business:
        return "📋 ЗАДАЧИ НА СЕГОДНЯ\n\nНет активных задач 👍"

    # Header
    today_formatted = today.strftime("%d %B")
    message = f"📋 ЗАДАЧИ НА СЕГОДНЯ ({today_formatted})\n"

    # Group by business
    for business_id, tasks in tasks_by_business.items():
        business_name = BUSINESS_NAMES[business_id]
        message += f"\n{business_name}\n"

        for task in tasks:
            task_line = format_task_line(task)
            message += f"{task_line}\n"

    # Summary stats
    total_tasks = sum(len(tasks) for tasks in tasks_by_business.values())
    high_priority = sum(
        1 for tasks in tasks_by_business.values()
        for task in tasks if task.priority == 1
    )
    medium_priority = sum(
        1 for tasks in tasks_by_business.values()
        for task in tasks if task.priority == 2
    )
    low_priority = sum(
        1 for tasks in tasks_by_business.values()
        for task in tasks if task.priority == 3
    )

    message += f"\nВсего: {total_tasks} задач"
    if high_priority:
        message += f" ({high_priority} срочных"
    if medium_priority:
        if high_priority:
            message += f", {medium_priority} средних"
        else:
            message += f" ({medium_priority} средних"
    if low_priority:
        if high_priority or medium_priority:
            message += f", {low_priority} низких"
        else:
            message += f" ({low_priority} низких"

    if high_priority or medium_priority or low_priority:
        message += ")"

    return message


async def send_daily_summary_to_user(
    bot: Bot,
    user_telegram_id: int,
    session: AsyncSession,
    user_id: int
) -> None:
    """Send daily summary to user via Telegram.

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
        message = await generate_daily_summary(session, user_id)

        # Send to user
        await bot.send_message(
            chat_id=user_telegram_id,
            text=message,
            parse_mode=None  # Plain text, no markdown
        )

        logger.info(
            "daily_summary_sent",
            user_id=user_id,
            telegram_id=user_telegram_id,
            task_count=message.count("🔴") + message.count("🟡") + message.count("🟢")
        )

    except Exception as e:
        logger.error(
            "daily_summary_send_failed",
            user_id=user_id,
            telegram_id=user_telegram_id,
            error=str(e)
        )
        raise
