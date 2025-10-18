"""
Business Domain Models - Business Planner.

The 4 fixed business contexts (bounded contexts).

Reference: docs/04-domain/bounded-contexts.md
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict


class Business(BaseModel):
    """Business context entity.
    
    Represents one of 4 bounded contexts (ADR-003):
    1. Inventum - Dental equipment repair
    2. Inventum Lab - Dental laboratory
    3. R&D - Research & Development
    4. Import & Trade - Equipment import
    
    Fixed set - only 4 businesses exist.
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    # Identity
    id: int = Field(..., ge=1, le=4, description="Fixed ID (1-4)")
    
    # Names
    name: str = Field(
        ...,
        pattern="^(inventum|lab|r&d|trade)$",
        description="Internal name"
    )
    display_name: str = Field(..., description="Display name")
    
    # Description
    description: str | None = None
    
    # AI Detection
    keywords: list[str] = Field(
        default_factory=list,
        description="Keywords for AI context detection"
    )
    
    # UI
    color: str | None = Field(
        None,
        pattern="^#[0-9A-Fa-f]{6}$",
        description="Hex color for UI"
    )
    
    # Status
    is_active: bool = Field(default=True)
    
    @field_validator("id")
    @classmethod
    def validate_fixed_id(cls, v: int) -> int:
        """Business IDs are fixed 1-4."""
        if v not in [1, 2, 3, 4]:
            raise ValueError("Business ID must be 1, 2, 3, or 4")
        return v
    
    @field_validator("name")
    @classmethod
    def validate_fixed_name(cls, v: str) -> str:
        """Business names are fixed."""
        valid_names = ["inventum", "lab", "r&d", "trade"]
        if v not in valid_names:
            raise ValueError(f"Business name must be one of: {valid_names}")
        return v
    
    def matches_keywords(self, text: str) -> int:
        """Count keyword matches in text (for AI detection).
        
        Args:
            text: Text to check (transcript, title, etc.)
            
        Returns:
            Number of matching keywords
            
        Example:
            >>> business.matches_keywords("Нужно починить фрезер")
            2  # "починить" and "фрезер" match
        """
        text_lower = text.lower()
        return sum(1 for keyword in self.keywords if keyword in text_lower)

