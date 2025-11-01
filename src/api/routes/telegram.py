"""
Telegram Webhook Routes - Business Planner.

Webhook endpoint for receiving updates from Telegram.

Reference:
- ADR-007 (Telegram Architecture - Webhooks)
- docs/08-infrastructure/security/security-strategy.md
"""

from fastapi import APIRouter, Request, HTTPException, Header, status
from telegram import Update

from src.config import settings
from src.utils.logger import logger
from src.telegram.bot import create_bot_application


router = APIRouter()


# Create global bot application instance
# This is initialized once and reused for all webhook requests
bot_app = None


async def get_bot_application():
    """Get or create bot application instance.
    
    Lazy initialization to avoid creating app during imports.
    
    Returns:
        Telegram Application instance
    """
    
    global bot_app
    
    if bot_app is None:
        bot_app = create_bot_application()
        await bot_app.initialize()
        logger.info("telegram_bot_application_initialized_for_webhook")
    
    return bot_app


# ============================================================================
# Webhook Endpoint
# ============================================================================

@router.post("/")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(None)
) -> dict:
    """Handle incoming webhook updates from Telegram.
    
    Security:
    - Verifies secret token (ADR-007)
    - Only accepts POST requests
    - Validates update structure
    
    Args:
        request: FastAPI request with Telegram update
        x_telegram_bot_api_secret_token: Secret token from Telegram header
        
    Returns:
        Success response
        
    Raises:
        HTTPException: If unauthorized or invalid update
        
    Reference: ADR-007 (Webhook security)
    """
    
    # Security: Verify secret token
    if settings.telegram_use_webhook:
        expected_token = settings.telegram_secret_token
        
        if not expected_token or x_telegram_bot_api_secret_token != expected_token:
            logger.warning(
                "webhook_unauthorized_attempt",
                provided_token=x_telegram_bot_api_secret_token[:10] + "..."
                if x_telegram_bot_api_secret_token else None
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid secret token"
            )
    
    # Parse update
    try:
        update_dict = await request.json()
        update = Update.de_json(update_dict, bot=(await get_bot_application()).bot)
        
    except Exception as e:
        logger.error("webhook_invalid_update", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid update format"
        )
    
    # Log update (in debug mode)
    if settings.debug:
        logger.debug(
            "webhook_update_received",
            update_id=update.update_id,
            message_type=update.message.text[:50] if update.message and update.message.text else None,
            voice_duration=update.message.voice.duration if update.message and update.message.voice else None,
            callback_data=update.callback_query.data if update.callback_query else None
        )
    else:
        logger.info(
            "webhook_update_received",
            update_id=update.update_id
        )
    
    # Process update through bot handlers
    try:
        app = await get_bot_application()
        await app.process_update(update)
        
        logger.info(
            "webhook_update_processed",
            update_id=update.update_id
        )
        
    except Exception as e:
        logger.error(
            "webhook_processing_failed",
            update_id=update.update_id,
            error=str(e),
            exc_info=True
        )
        
        # Don't raise exception to Telegram (acknowledge receipt)
        # Error will be handled by bot's error handler
    
    # Always return 200 OK to Telegram
    return {"ok": True}


# ============================================================================
# Webhook Management Endpoints
# ============================================================================

@router.post("/set-webhook")
async def set_webhook() -> dict:
    """Set Telegram webhook URL (admin endpoint).
    
    Should be called once during deployment.
    
    Returns:
        Webhook configuration details
        
    Reference: ADR-007 (Webhook setup)
    """
    
    if not settings.telegram_use_webhook:
        return {
            "status": "webhook_disabled",
            "message": "Webhook is disabled in settings"
        }
    
    app = await get_bot_application()
    
    webhook_url = settings.telegram_webhook_url
    secret_token = settings.telegram_secret_token
    
    try:
        await app.bot.set_webhook(
            url=webhook_url,
            secret_token=secret_token,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
        
        logger.info(
            "webhook_set_successfully",
            url=webhook_url
        )
        
        return {
            "status": "success",
            "webhook_url": webhook_url,
            "secret_token_set": bool(secret_token)
        }
        
    except Exception as e:
        logger.error("webhook_setup_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set webhook: {str(e)}"
        )


@router.get("/webhook-info")
async def get_webhook_info() -> dict:
    """Get current webhook configuration (admin endpoint).
    
    Returns:
        Webhook information from Telegram
    """
    
    app = await get_bot_application()
    
    try:
        webhook_info = await app.bot.get_webhook_info()
        
        return {
            "url": webhook_info.url,
            "has_custom_certificate": webhook_info.has_custom_certificate,
            "pending_update_count": webhook_info.pending_update_count,
            "last_error_date": webhook_info.last_error_date,
            "last_error_message": webhook_info.last_error_message,
            "max_connections": webhook_info.max_connections,
            "allowed_updates": webhook_info.allowed_updates
        }
        
    except Exception as e:
        logger.error("failed_to_get_webhook_info", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get webhook info: {str(e)}"
        )


@router.delete("/webhook")
async def delete_webhook() -> dict:
    """Delete webhook (admin endpoint).
    
    Useful for switching to polling mode or troubleshooting.
    
    Returns:
        Success confirmation
    """
    
    app = await get_bot_application()
    
    try:
        await app.bot.delete_webhook()
        
        logger.info("webhook_deleted")
        
        return {
            "status": "success",
            "message": "Webhook deleted"
        }
        
    except Exception as e:
        logger.error("webhook_deletion_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete webhook: {str(e)}"
        )

