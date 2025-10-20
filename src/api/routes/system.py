"""
System API Routes - Business Planner.

Health checks, businesses, members, system info.

Reference: docs/03-api/openapi.yaml
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models import Business, Member
from src.infrastructure.database import get_session, check_database_health
from src.utils.logger import logger
from src.services import trigger_daily_summary_now


router = APIRouter()


@router.get("/health")
async def health_check():
    """System health check.
    
    Checks:
    - Application running
    - Database connection
    - TODO: Redis connection
    - TODO: OpenAI API
    
    Returns:
        Health status dict
    """
    
    checks = {
        "status": "healthy",
        "database": await check_database_health(),
        "redis": "not_implemented",      # TODO
        "openai_api": "not_implemented"  # TODO
    }
    
    # Overall status
    all_healthy = checks["database"] is True
    
    if all_healthy:
        return {"status": "healthy", "checks": checks}
    else:
        return {"status": "degraded", "checks": checks}


@router.get("/businesses", response_model=list[Business])
async def list_businesses(
    session: AsyncSession = Depends(get_session)
) -> list[Business]:
    """Get the 4 business contexts.
    
    Returns:
        List of 4 businesses
    """
    
    from src.infrastructure.database.models import BusinessORM
    from sqlalchemy import select
    
    result = await session.execute(
        select(BusinessORM).order_by(BusinessORM.id)
    )
    businesses_orm = result.scalars().all()
    
    return [Business.model_validate(b) for b in businesses_orm]


@router.get("/members", response_model=list[Member])
async def list_members(
    business_id: int | None = None,
    session: AsyncSession = Depends(get_session)
) -> list[Member]:
    """Get team members (8 people).
    
    Args:
        business_id: Optional filter by business
        
    Returns:
        List of members
    """
    
    from src.infrastructure.database.models import MemberORM
    from sqlalchemy import select
    
    query = select(MemberORM)
    
    # TODO: Filter by business_id if provided
    # (Need to check if business_id in member.business_ids array)
    
    result = await session.execute(query.order_by(MemberORM.name))
    members_orm = result.scalars().all()
    
    return [Member.model_validate(m) for m in members_orm]


@router.post("/trigger-daily-summary")
async def trigger_daily_summary():
    """Manually trigger daily summary (for testing).

    Sends daily task summary to user immediately.

    Returns:
        Success message
    """
    try:
        await trigger_daily_summary_now()
        return {"status": "success", "message": "Daily summary sent"}
    except Exception as e:
        logger.error("manual_trigger_failed", error=str(e))
        return {"status": "error", "message": str(e)}


@router.delete("/tasks/clear-all")
async def clear_all_tasks(
    user_id: int = 1,
    session: AsyncSession = Depends(get_session)
):
    """Clear all tasks for user (for testing/development only).

    WARNING: This permanently deletes all tasks!

    Args:
        user_id: User ID (default 1)
        session: Database session

    Returns:
        Number of deleted tasks
    """
    try:
        from src.infrastructure.database.models import TaskORM
        from sqlalchemy import delete

        # Delete all tasks for user
        stmt = delete(TaskORM).where(TaskORM.user_id == user_id)
        result = await session.execute(stmt)
        await session.commit()

        deleted_count = result.rowcount

        logger.info("all_tasks_cleared", user_id=user_id, count=deleted_count)

        return {
            "status": "success",
            "message": f"Deleted {deleted_count} tasks",
            "deleted_count": deleted_count
        }

    except Exception as e:
        logger.error("clear_tasks_failed", error=str(e))
        await session.rollback()
        return {"status": "error", "message": str(e)}

