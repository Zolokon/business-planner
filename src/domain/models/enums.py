"""
Domain Enums - Business Planner.

Core enumerations used across the domain model.

Reference: docs/04-domain/value-objects.md
"""

from enum import IntEnum, Enum


class BusinessID(IntEnum):
    """The 4 business context identifiers.
    
    Each business is a separate bounded context (ADR-003).
    Fixed set - never changes.
    
    Reference: docs/04-domain/bounded-contexts.md
    """
    
    INVENTUM = 1  # Dental equipment repair
    LAB = 2       # Dental laboratory
    R_D = 3       # Research & Development
    TRADE = 4     # Import & Trade
    
    @property
    def display_name(self) -> str:
        """Human-readable business name."""
        names = {
            BusinessID.INVENTUM: "Inventum",
            BusinessID.LAB: "Inventum Lab",
            BusinessID.R_D: "R&D",
            BusinessID.TRADE: "Import & Trade"
        }
        return names[self]
    
    @property
    def emoji(self) -> str:
        """Emoji for Telegram display."""
        emojis = {
            BusinessID.INVENTUM: "🔧",
            BusinessID.LAB: "🦷",
            BusinessID.R_D: "🔬",
            BusinessID.TRADE: "💼"
        }
        return emojis[self]


class Priority(IntEnum):
    """Task priority based on Eisenhower Matrix.
    
    Combines importance and urgency:
    - 1: DO NOW (Important + Urgent)
    - 2: SCHEDULE (Important + Not Urgent) - default
    - 3: DELEGATE (Not Important + Urgent)
    - 4: BACKLOG (Not Important + Not Urgent)
    
    Reference: docs/04-domain/value-objects.md
    """
    
    DO_NOW = 1      # 🔴 Important + Urgent
    SCHEDULE = 2    # 🟡 Important + Not Urgent (default)
    DELEGATE = 3    # 🟠 Not Important + Urgent
    BACKLOG = 4     # 🟢 Not Important + Not Urgent
    
    @property
    def display_name(self) -> str:
        """Human-readable priority name."""
        names = {
            Priority.DO_NOW: "Срочно",
            Priority.SCHEDULE: "Запланировать",
            Priority.DELEGATE: "Делегировать",
            Priority.BACKLOG: "Когда-нибудь"
        }
        return names[self]
    
    @property
    def emoji(self) -> str:
        """Emoji for Telegram display."""
        emojis = {
            Priority.DO_NOW: "🔴",
            Priority.SCHEDULE: "🟡",
            Priority.DELEGATE: "🟠",
            Priority.BACKLOG: "🟢"
        }
        return emojis[self]
    
    @classmethod
    def from_importance_urgency(
        cls, 
        is_important: bool, 
        is_urgent: bool
    ) -> "Priority":
        """Calculate priority from importance and urgency.
        
        Args:
            is_important: Task is important
            is_urgent: Task is urgent
            
        Returns:
            Priority level (1-4)
            
        Example:
            >>> Priority.from_importance_urgency(True, True)
            <Priority.DO_NOW: 1>
        """
        if is_important and is_urgent:
            return cls.DO_NOW
        elif is_important and not is_urgent:
            return cls.SCHEDULE
        elif not is_important and is_urgent:
            return cls.DELEGATE
        else:
            return cls.BACKLOG


class TaskStatus(str, Enum):
    """Task status - lifecycle state.
    
    Allowed transitions:
    - OPEN → DONE
    - DONE → ARCHIVED
    - DONE → OPEN (reopen)
    
    Forbidden:
    - OPEN → ARCHIVED (must complete first)
    - ARCHIVED → anything (final state)
    """
    
    OPEN = "open"          # 🔵 Active, not done
    DONE = "done"          # ✅ Completed
    ARCHIVED = "archived"  # 📦 Completed and archived
    
    @property
    def emoji(self) -> str:
        """Emoji representation."""
        emojis = {
            TaskStatus.OPEN: "🔵",
            TaskStatus.DONE: "✅",
            TaskStatus.ARCHIVED: "📦"
        }
        return emojis[self]
    
    def can_transition_to(self, new_status: "TaskStatus") -> bool:
        """Check if transition is allowed.
        
        Args:
            new_status: Target status
            
        Returns:
            True if transition is valid
            
        Reference: docs/04-domain/business-rules.md (Rule 13.1)
        """
        allowed_transitions = {
            TaskStatus.OPEN: [TaskStatus.DONE],
            TaskStatus.DONE: [TaskStatus.ARCHIVED, TaskStatus.OPEN],
            TaskStatus.ARCHIVED: []  # Final state
        }
        return new_status in allowed_transitions.get(self, [])


class ProjectStatus(str, Enum):
    """Project status - lifecycle state."""
    
    ACTIVE = "active"        # 🟢 Currently working on
    ON_HOLD = "on_hold"      # ⏸️ Paused
    COMPLETED = "completed"  # ✅ Done
    
    @property
    def emoji(self) -> str:
        """Emoji representation."""
        emojis = {
            ProjectStatus.ACTIVE: "🟢",
            ProjectStatus.ON_HOLD: "⏸️",
            ProjectStatus.COMPLETED: "✅"
        }
        return emojis[self]


class HistoryAction(str, Enum):
    """Action types for task history (audit trail)."""
    
    CREATED = "created"      # Task created
    UPDATED = "updated"      # Task modified
    COMPLETED = "completed"  # Task marked done
    DELETED = "deleted"      # Task deleted
    ARCHIVED = "archived"    # Task archived


class Confidence(str, Enum):
    """Confidence level in time estimate.
    
    Based on number of similar tasks found in RAG search.
    """
    
    HIGH = "high"      # 3+ similar tasks
    MEDIUM = "medium"  # 1-2 similar tasks
    LOW = "low"        # No similar tasks (default)

