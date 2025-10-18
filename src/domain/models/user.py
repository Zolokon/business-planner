"""
User Domain Models - Business Planner.

Telegram users of the system.
Currently: 1 user (Константин)

Reference: docs/04-domain/entities.md (User Entity)
"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class User(BaseModel):
    """User entity - Telegram user.
    
    Represents users who can create tasks and projects.
    Currently: Single user (Константин, CEO)
    Future: Can add team members with accounts.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    # Identity
    id: int
    telegram_id: int = Field(..., description="Telegram user ID (unique)")
    
    # Profile
    name: str = Field(..., min_length=1, max_length=100)
    username: str | None = Field(None, description="Telegram username (@konstantin)")
    
    # Settings
    timezone: str = Field(
        default="Asia/Almaty",
        description="User timezone (UTC+5 for Almaty)"
    )
    preferences: dict = Field(
        default_factory=dict,
        description="User preferences (JSON)"
    )
    
    # Activity
    created_at: datetime
    last_active: datetime
    
    def set_preference(self, key: str, value: any) -> None:
        """Set user preference.
        
        Args:
            key: Preference key
            value: Preference value
            
        Example:
            >>> user.set_preference("default_business", "inventum")
        """
        self.preferences[key] = value
    
    def get_preference(self, key: str, default: any = None) -> any:
        """Get user preference with default.
        
        Args:
            key: Preference key
            default: Default value if not found
            
        Returns:
            Preference value or default
        """
        return self.preferences.get(key, default)

