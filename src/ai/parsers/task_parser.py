"""
Task Parser - Business Planner.

Parse voice/text into structured task using GPT-5 Nano.

Reference:
- ADR-002 (GPT-5 Nano)
- docs/05-ai-specifications/prompts/task-parser.md
"""

from pydantic import BaseModel

from src.domain.models import TaskCreate
from src.infrastructure.external.openai_client import openai_client
from src.utils.logger import logger


class ParsedTask(BaseModel):
    """Parsed task data from AI (GPT-5 Nano output).
    
    Reference: docs/03-api/pydantic-models.md
    """
    
    title: str
    business_id: int
    deadline_text: str | None = None
    project_name: str | None = None
    assigned_to_name: str | None = None
    priority: int = 2
    description: str | None = None


async def parse_task_from_transcript(
    transcript: str,
    user_id: int
) -> ParsedTask:
    """Parse task from voice transcript or text using GPT-5 Nano.
    
    Args:
        transcript: Voice transcript or text message
        user_id: User ID for context
        
    Returns:
        ParsedTask with structured data
        
    Raises:
        ValueError: If parsing fails
        
    Example:
        >>> parsed = await parse_task_from_transcript(
        ...     "Дима должен починить фрезер завтра утром",
        ...     user_id=1
        ... )
        >>> print(parsed.title)
        "Починить фрезер"
        >>> print(parsed.business_id)
        1  # Inventum
    """
    
    logger.info("parsing_task", transcript=transcript, user_id=user_id)
    
    try:
        # Call GPT-5 Nano
        parsed_data = await openai_client.parse_task(
            transcript=transcript,
            context=None  # TODO: Add user context (recent tasks, projects)
        )
        
        # Validate and create ParsedTask
        parsed_task = ParsedTask(**parsed_data)
        
        logger.info(
            "task_parsed",
            title=parsed_task.title,
            business_id=parsed_task.business_id,
            assigned_to=parsed_task.assigned_to_name
        )
        
        return parsed_task
        
    except Exception as e:
        logger.error("task_parsing_failed", error=str(e), transcript=transcript)
        raise ValueError(f"Failed to parse task: {str(e)}")

