"""
Business Planner - FastAPI Application Entry Point.

Voice-first task management system for 4 businesses via Telegram bot.

Tech Stack:
- FastAPI + LangGraph + PostgreSQL + GPT-5 Nano + Digital Ocean

Reference: 
- START_HERE.md for project context
- .cursorrules for coding standards
- docs/ for complete specifications
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.config import settings
from src.utils.logger import setup_logging, logger
from src.api.routes import tasks, system, telegram
from src.infrastructure.database import init_database, close_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events.
    
    Startup:
    - Initialize database connection
    - Initialize Redis connection
    - Set Telegram webhook (if production)
    
    Shutdown:
    - Close database connections
    - Close Redis connections
    - Remove Telegram webhook
    """
    
    # Startup
    logger.info(
        "application_starting",
        environment=settings.environment,
        debug=settings.debug
    )

    # Initialize database
    # TEMP: Skipping DB init on Windows due to asyncpg issues
    # await init_database()
    logger.info("database_initialization_skipped", reason="Windows asyncpg compatibility")
    
    # TODO: Initialize Redis
    # await redis_client.connect()
    
    # TODO: Set Telegram webhook (production only)
    # if settings.is_production and settings.telegram_use_webhook:
    #     await setup_telegram_webhook()
    
    logger.info("application_started")
    
    yield  # Application runs
    
    # Shutdown
    logger.info("application_shutting_down")
    
    # Close database connections
    await close_database()
    
    # TODO: Close Redis
    # await redis_client.close()
    
    logger.info("application_stopped")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Business Planner API",
    description="Voice-first task management for 4 businesses",
    version="1.0.0",
    docs_url="/docs" if settings.is_development else None,  # Swagger UI (dev only)
    redoc_url="/redoc" if settings.is_development else None,
    lifespan=lifespan
)

# ============================================================================
# Middleware
# ============================================================================

# CORS (for future Web UI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else ["https://planner.yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Routes
# ============================================================================

# Include routers
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(system.router, tags=["system"])
app.include_router(telegram.router, prefix="/webhook", tags=["telegram"])

# TODO: Implement and include
# app.include_router(projects.router, prefix="/projects", tags=["projects"])
# app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])


# ============================================================================
# Basic Endpoints (Temporary)
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": "Business Planner",
        "version": "1.0.0",
        "status": "Phase 1 - Development",
        "environment": settings.environment
    }


# Health check is now in system.router at /health


# ============================================================================
# Startup
# ============================================================================

def main():
    """Run application (for development)."""
    import uvicorn
    import logging
    
    # Setup logging
    setup_logging(debug=settings.debug)
    
    logger.info(
        "starting_uvicorn",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        debug_mode=settings.debug
    )
    
    # Suppress uvicorn default logs in non-debug mode
    if not settings.debug:
        logging.getLogger("uvicorn").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_config=None  # Use our custom logging
    )


if __name__ == "__main__":
    main()

