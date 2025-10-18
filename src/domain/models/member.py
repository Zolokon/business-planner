"""
Member Domain Models - Business Planner.

Team members working across 4 businesses.
Total: 8 people (see docs/TEAM.md).

Reference: docs/04-domain/entities.md (Member Entity)
"""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict


class Member(BaseModel):
    """Team member entity.
    
    Represents people working in one or more businesses.
    Can be cross-functional (Максим, Дима work in Inventum + R&D).
    
    Total team size: 8 people
    - Константин (CEO, all businesses)
    - Лиза (Marketing, all businesses)
    - Максим (Inventum + R&D)
    - Дима (Inventum + R&D)
    - Максут (Inventum only)
    - Юрий Владимирович (Lab only)
    - Мария (Lab only)
    - Слава (Trade only)
    
    Reference: docs/TEAM.md
    """
    
    model_config = ConfigDict(from_attributes=True)
    
    # Identity
    id: int
    
    # Profile
    name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., description="Директор, Мастер, CAD/CAM, etc.")
    
    # Business associations
    business_ids: list[int] = Field(
        ...,
        description="Businesses this member works in (1-4)"
    )
    
    # Skills
    skills: list[str] = Field(
        default_factory=list,
        description="Skills for task assignment"
    )
    
    # Flags
    is_cross_functional: bool = Field(
        default=False,
        description="Works in 2+ businesses"
    )
    
    # Notes
    notes: str | None = None
    created_at: datetime | None = None
    
    @field_validator("business_ids")
    @classmethod
    def validate_business_ids(cls, v: list[int]) -> list[int]:
        """Validate all business IDs are valid (1-4).
        
        Args:
            v: List of business IDs
            
        Returns:
            Validated list
            
        Raises:
            ValueError: If any business_id is invalid
        """
        if not v:
            raise ValueError("Member must work in at least one business")
        
        for bid in v:
            if bid not in [1, 2, 3, 4]:
                raise ValueError(f"Invalid business_id: {bid}. Must be 1-4")
        
        return v
    
    @property
    def business_count(self) -> int:
        """Number of businesses member works in."""
        return len(self.business_ids)
    
    def works_in_business(self, business_id: int) -> bool:
        """Check if member works in specific business.
        
        Args:
            business_id: Business to check (1-4)
            
        Returns:
            True if member works in this business
        """
        return business_id in self.business_ids

