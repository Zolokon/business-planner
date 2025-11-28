"""
Task Scheduler - Business Planner.

Handles scheduled tasks like daily summaries, weekly analytics, etc.

Uses APScheduler for cron-like scheduling.

Reference:
- Daily summary at 9:30 AM
- Weekly analytics on Fridays
"""

import asyncio
from datetime import time as dt_time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot

from src.config import settings
from src.utils.logger import logger
from src.infrastructure.database import get_session
from src.services.daily_summary import send_daily_summary_to_user
from src.services.evening_summary import send_evening_summary_to_user


# ============================================================================
# Scheduler Instance
# ============================================================================

scheduler: AsyncIOScheduler | None = None


# ============================================================================
# Scheduled Tasks
# ============================================================================

async def daily_summary_job():
    """Send daily task summary to all users at 9:30 AM.

    Runs every day at 9:30 AM local time (Almaty timezone: UTC+5).
    Does not send if there are no tasks.
    """
    logger.info("daily_summary_job_started")

    try:
        # Get bot instance
        bot = Bot(token=settings.telegram_bot_token)

        # Get database session
        session_gen = get_session()
        session = await anext(session_gen)

        try:
            # For now, send to user ID 1 (CEO)
            # TODO: In future, fetch all active users from database
            user_id = 1
            user_telegram_id = 1802270374  # CEO's Telegram ID (KZ_workshop)

            await send_daily_summary_to_user(
                bot=bot,
                user_telegram_id=user_telegram_id,
                session=session,
                user_id=user_id
            )

            logger.info("daily_summary_job_completed")

        finally:
            await session.close()

    except Exception as e:
        logger.error("daily_summary_job_failed", error=str(e), exc_info=True)


async def evening_summary_job():
    """Send evening task summary to all users at 7 PM.

    Shows incomplete tasks with quick action buttons.
    Runs every day at 19:00 (7 PM) local time (Almaty timezone: UTC+5).
    """
    logger.info("evening_summary_job_started")

    try:
        # Get bot instance
        bot = Bot(token=settings.telegram_bot_token)

        # Get database session
        session_gen = get_session()
        session = await anext(session_gen)

        try:
            # For now, send to user ID 1 (CEO)
            # TODO: In future, fetch all active users from database
            user_id = 1
            user_telegram_id = 1802270374  # CEO's Telegram ID (KZ_workshop)

            await send_evening_summary_to_user(
                bot=bot,
                user_telegram_id=user_telegram_id,
                session=session,
                user_id=user_id
            )

            logger.info("evening_summary_job_completed")

        finally:
            await session.close()

    except Exception as e:
        logger.error("evening_summary_job_failed", error=str(e), exc_info=True)


async def weekly_analytics_job():
    """Send weekly analytics on Fridays.

    Placeholder for future implementation.
    """
    logger.info("weekly_analytics_job_started")
    # TODO: Implement weekly analytics
    logger.info("weekly_analytics_job_not_implemented")


# ============================================================================
# Scheduler Lifecycle
# ============================================================================

def init_scheduler() -> AsyncIOScheduler:
    """Initialize and configure scheduler.

    Returns:
        Configured scheduler instance
    """
    logger.info("initializing_scheduler")

    # Create scheduler with asyncio executor
    scheduler_instance = AsyncIOScheduler(timezone="Asia/Almaty")

    # Add daily summary job (9:30 AM every day)
    scheduler_instance.add_job(
        daily_summary_job,
        trigger=CronTrigger(hour=9, minute=30, timezone="Asia/Almaty"),
        id="daily_summary",
        name="Daily Task Summary",
        replace_existing=True
    )

    # Add evening summary job (7 PM every day)
    scheduler_instance.add_job(
        evening_summary_job,
        trigger=CronTrigger(hour=19, minute=0, timezone="Asia/Almaty"),
        id="evening_summary",
        name="Evening Task Summary",
        replace_existing=True
    )

    # Add weekly analytics job (Fridays at 5 PM)
    scheduler_instance.add_job(
        weekly_analytics_job,
        trigger=CronTrigger(day_of_week="fri", hour=17, minute=0, timezone="Asia/Almaty"),
        id="weekly_analytics",
        name="Weekly Analytics",
        replace_existing=True
    )

    logger.info(
        "scheduler_initialized",
        jobs_count=len(scheduler_instance.get_jobs())
    )

    return scheduler_instance


def start_scheduler():
    """Start the scheduler.

    Should be called during application startup.
    """
    global scheduler

    if scheduler is not None:
        logger.warning("scheduler_already_running")
        return

    scheduler = init_scheduler()
    scheduler.start()

    logger.info("scheduler_started")


def stop_scheduler():
    """Stop the scheduler.

    Should be called during application shutdown.
    """
    global scheduler

    if scheduler is None:
        logger.warning("scheduler_not_running")
        return

    scheduler.shutdown(wait=False)
    scheduler = None

    logger.info("scheduler_stopped")


def get_scheduler() -> AsyncIOScheduler | None:
    """Get current scheduler instance.

    Returns:
        Scheduler instance or None if not started
    """
    return scheduler


# ============================================================================
# Manual Trigger (for testing)
# ============================================================================

async def trigger_daily_summary_now():
    """Manually trigger daily summary (for testing).

    Usage:
        From FastAPI endpoint or CLI:
        await trigger_daily_summary_now()
    """
    logger.info("manual_daily_summary_triggered")
    await daily_summary_job()


async def trigger_evening_summary_now():
    """Manually trigger evening summary (for testing).

    Usage:
        From FastAPI endpoint or CLI:
        await trigger_evening_summary_now()
    """
    logger.info("manual_evening_summary_triggered")
    await evening_summary_job()
