"""
SQLAlchemy ORM Models - Business Planner.

Database models mapping to PostgreSQL tables.

Reference: docs/02-database/schema.sql
"""

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, TIMESTAMP,
    ForeignKey, CheckConstraint, ARRAY, JSON
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy import event
from sqlalchemy.engine import Engine
import os

# Use JSON for SQLite (tests), JSONB for PostgreSQL (production)
_is_sqlite = os.environ.get('DATABASE_URL', '').startswith('sqlite')
JSONType = JSON if _is_sqlite else JSONB

# For arrays: use JSON for SQLite, ARRAY for PostgreSQL
def ArrayType(item_type):
    """Get appropriate array type based on database."""
    if _is_sqlite:
        return JSON  # Store as JSON array in SQLite
    return ARRAY(item_type)

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    # For SQLite tests without pgvector
    Vector = None

from src.infrastructure.database.connection import Base


# ============================================================================
# Users
# ============================================================================

class UserORM(Base):
    """User table - Telegram users.
    
    Maps to: users table
    Reference: docs/02-database/schema.sql
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    username = Column(String(100))
    timezone = Column(String(50), default="Asia/Almaty", nullable=False)
    preferences = Column(JSONType, default={}, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    last_active = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


# ============================================================================
# Businesses
# ============================================================================

class BusinessORM(Base):
    """Business table - The 4 business contexts.
    
    Maps to: businesses table
    Fixed 4 businesses (ADR-003).
    """
    
    __tablename__ = "businesses"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    keywords = Column(ArrayType(Text), default=[], nullable=False)
    color = Column(String(7))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


# ============================================================================
# Members
# ============================================================================

class MemberORM(Base):
    """Member table - Team members (8 people).
    
    Maps to: members table
    Reference: docs/TEAM.md
    """
    
    __tablename__ = "members"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    role = Column(String(200))
    business_ids = Column(ArrayType(Integer), nullable=False, default=[])
    skills = Column(ArrayType(Text), default=[])
    is_cross_functional = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


# ============================================================================
# Projects
# ============================================================================

class ProjectORM(Base):
    """Project table - User-created task groupings.
    
    Maps to: projects table
    """
    
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="RESTRICT"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(
        String(20),
        default="active",
        nullable=False,
        server_default="active"
    )
    deadline = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(TIMESTAMP(timezone=True))
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'on_hold', 'completed')",
            name="valid_project_status"
        ),
    )


# ============================================================================
# Tasks (Main Entity)
# ============================================================================

class TaskORM(Base):
    """Task table - Main entity.
    
    Maps to: tasks table
    
    CRITICAL: business_id is MANDATORY (ADR-003 - Business Isolation)
    """
    
    __tablename__ = "tasks"
    
    # Identity
    id = Column(Integer, primary_key=True)
    
    # Ownership
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    business_id = Column(
        Integer,
        ForeignKey("businesses.id", ondelete="RESTRICT"),
        nullable=False,  # CRITICAL: Mandatory (ADR-003)
        index=True
    )
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"))
    assigned_to = Column(Integer, ForeignKey("members.id", ondelete="SET NULL"))
    
    # Content
    title = Column(Text, nullable=False)
    description = Column(Text)
    
    # Status & Priority
    status = Column(String(20), default="open", nullable=False, index=True)
    priority = Column(Integer, default=2, nullable=False)
    
    # Time tracking
    estimated_duration = Column(Integer)  # Minutes
    actual_duration = Column(Integer)     # Minutes (for learning)
    
    # Dates
    deadline = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(TIMESTAMP(timezone=True))
    
    # AI/ML - Vector embedding (1536 dimensions)
    # Use JSON array for SQLite (tests), Vector for PostgreSQL (production)
    embedding = Column(Vector(1536) if Vector else JSON)

    # Flexible metadata
    task_metadata = Column(JSONType, default={})
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('open', 'done', 'archived')", name="valid_status"),
        CheckConstraint("priority BETWEEN 1 AND 4", name="valid_priority"),
        CheckConstraint(
            "estimated_duration IS NULL OR estimated_duration BETWEEN 1 AND 480",
            name="valid_estimated_duration"
        ),
        CheckConstraint(
            "actual_duration IS NULL OR actual_duration BETWEEN 1 AND 480",
            name="valid_actual_duration"
        ),
    )


# ============================================================================
# Task History (Audit Trail)
# ============================================================================

class TaskHistoryORM(Base):
    """Task history table - Audit trail and analytics.
    
    Maps to: task_history table
    Automatically populated by database triggers.
    """
    
    __tablename__ = "task_history"
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(50), nullable=False)
    changes = Column(JSONType, default={})
    duration = Column(Integer)  # Actual duration if completed
    occurred_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        CheckConstraint(
            "action IN ('created', 'updated', 'completed', 'deleted', 'archived')",
            name="valid_action"
        ),
    )

