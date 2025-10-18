"""
Configuration management for Business Planner.

Uses pydantic-settings for type-safe configuration from environment variables.
All secrets loaded from environment (never hardcoded).

Reference: .cursorrules (Environment Variables section)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    All settings have defaults except secrets (API keys, tokens).
    Load from .env file in development, from environment in production.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # =========================================================================
    # Application
    # =========================================================================
    environment: str = Field(default="development", description="development|production")
    debug: bool = Field(default=False, description="Enable debug mode (verbose logs)")
    log_level: str = Field(default="INFO", description="Logging level")
    
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    
    # =========================================================================
    # Database (PostgreSQL)
    # =========================================================================
    database_url: str = Field(
        ...,
        description="PostgreSQL connection string (required)"
    )
    db_pool_size: int = Field(default=5)
    db_max_overflow: int = Field(default=10)
    db_echo: bool = Field(default=False, description="Log SQL queries")
    
    # =========================================================================
    # Redis (Cache)
    # =========================================================================
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_password: str | None = Field(default=None)
    
    # =========================================================================
    # OpenAI
    # =========================================================================
    openai_api_key: str = Field(..., description="OpenAI API key (required)")
    openai_org_id: str | None = Field(default=None)
    
    # Model selection
    model_parser: str = Field(default="gpt-5-nano")
    model_reasoning: str = Field(default="gpt-5-nano")
    model_analytics: str = Field(default="gpt-5")
    model_voice: str = Field(default="whisper-1")
    model_embeddings: str = Field(default="text-embedding-3-small")
    
    # AI Configuration
    max_context_tokens: int = Field(default=100000, description="Max context for GPT-5 Nano")
    
    # =========================================================================
    # Telegram Bot
    # =========================================================================
    telegram_bot_token: str = Field(..., description="Telegram bot token (required)")
    telegram_secret_token: str = Field(
        ...,
        description="Secret token for webhook validation (required)"
    )
    telegram_webhook_url: str | None = Field(
        default=None,
        description="Webhook URL (production only)"
    )
    telegram_use_webhook: bool = Field(
        default=False,
        description="Use webhook (prod) or polling (dev)"
    )
    
    # =========================================================================
    # RAG Configuration (ADR-004)
    # =========================================================================
    embedding_dimension: int = Field(default=1536)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    rag_top_k: int = Field(default=5, ge=1, le=20)
    
    # =========================================================================
    # Business Rules
    # =========================================================================
    default_deadline_days: int = Field(default=7)
    workday_start_hour: int = Field(default=9)
    workday_end_hour: int = Field(default=18)
    timezone: str = Field(default="Asia/Almaty", description="UTC+5")
    
    # Time of day defaults (Russian phrases)
    time_morning: str = Field(default="09:00", description="'утром'")
    time_afternoon: str = Field(default="13:00", description="'днем'")
    time_evening: str = Field(default="18:00", description="'вечером'")
    
    # =========================================================================
    # Rate Limiting
    # =========================================================================
    rate_limit_per_minute: int = Field(default=30)
    rate_limit_per_hour: int = Field(default=500)
    
    # =========================================================================
    # Monitoring (Optional)
    # =========================================================================
    sentry_dsn: str | None = Field(default=None, description="Sentry error tracking")
    enable_metrics: bool = Field(default=True)
    
    # =========================================================================
    # Validators
    # =========================================================================
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        valid = ["development", "staging", "production"]
        if v not in valid:
            raise ValueError(f"environment must be one of: {valid}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid:
            raise ValueError(f"log_level must be one of: {valid}")
        return v.upper()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


# Global settings instance
settings = Settings()

