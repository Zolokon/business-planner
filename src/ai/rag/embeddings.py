"""
Embeddings Management - Business Planner.

Generate and manage vector embeddings for RAG.

Reference:
- ADR-004 (RAG Strategy)
- docs/02-database/schema.sql (vector column)
"""

from src.infrastructure.external.openai_client import openai_client
from src.infrastructure.database.repositories.task_repository import TaskRepository
from src.utils.logger import logger


async def generate_and_store_embedding(task_id: int, title: str, repository: TaskRepository) -> None:
    """Generate embedding for task and store in database.
    
    This is called AFTER task creation (async, doesn't block response).
    
    Args:
        task_id: Task ID
        title: Task title to embed
        repository: Task repository for database access
        
    Reference: ADR-004 (RAG Strategy section on Embedding Generation)
    """
    try:
        # Generate embedding
        embedding = await openai_client.generate_embedding(title)
        
        # Store in database
        await repository.update_embedding(task_id, embedding)
        
        logger.info(
            "embedding_stored",
            task_id=task_id,
            title_length=len(title),
            embedding_dimensions=len(embedding)
        )
        
    except Exception as e:
        # Non-critical error - task exists without embedding
        # Can be regenerated later
        logger.warning(
            "embedding_generation_failed",
            task_id=task_id,
            error=str(e),
            impact="Task created without embedding (can regenerate later)"
        )

