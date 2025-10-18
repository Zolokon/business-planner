"""
RAG Retriever - Business Planner.

Retrieve similar tasks for time estimation.

Reference:
- ADR-003 (Business Isolation - CRITICAL)
- ADR-004 (RAG Strategy)
"""

from src.domain.models import Task
from src.infrastructure.external.openai_client import openai_client
from src.infrastructure.database.repositories.task_repository import TaskRepository
from src.config import settings
from src.utils.logger import logger


class RAGRetriever:
    """RAG retriever for finding similar tasks.
    
    CRITICAL: Always filters by business_id (ADR-003).
    """
    
    def __init__(self, repository: TaskRepository):
        """Initialize retriever with task repository.
        
        Args:
            repository: Task repository for database access
        """
        self.repository = repository
    
    async def find_similar_tasks(
        self,
        task_title: str,
        business_id: int,
        top_k: int | None = None
    ) -> list[Task]:
        """Find similar completed tasks for learning.
        
        CRITICAL: MUST filter by business_id (ADR-003).
        This prevents cross-business contamination.
        
        Args:
            task_title: New task title
            business_id: Business context (MANDATORY)
            top_k: Number of results (default from settings)
            
        Returns:
            List of similar tasks (same business only)
            
        Example:
            >>> similar = await retriever.find_similar_tasks(
            ...     "Починить фрезер",
            ...     business_id=1
            ... )
            >>> # Returns only Inventum tasks, never Lab/R&D/Trade
        """
        # Validate business_id (paranoid validation)
        if business_id not in [1, 2, 3, 4]:
            raise ValueError(
                f"Invalid business_id: {business_id}. "
                "This violates ADR-003 (Business Isolation)"
            )
        
        if top_k is None:
            top_k = settings.rag_top_k
        
        try:
            # Generate embedding for query
            embedding = await openai_client.generate_embedding(task_title)
            
            # Search similar tasks (with business filter!)
            similar_tasks = await self.repository.find_similar(
                embedding=embedding,
                business_id=business_id,  # CRITICAL: Business isolation!
                limit=top_k,
                similarity_threshold=settings.similarity_threshold
            )
            
            # Paranoid validation (ADR-003)
            for task in similar_tasks:
                assert task.business_id == business_id, \
                    f"RAG isolation breach! Expected business {business_id}, " \
                    f"got {task.business_id}. This is a critical error (ADR-003)!"
            
            logger.info(
                "rag_retrieval_completed",
                task_title=task_title,
                business_id=business_id,
                similar_tasks_found=len(similar_tasks),
                top_k=top_k
            )
            
            return similar_tasks
            
        except Exception as e:
            logger.error(
                "rag_retrieval_failed",
                error=str(e),
                business_id=business_id
            )
            return []  # Return empty list (will use default estimate)


# Singleton instance
_retriever_instance: RAGRetriever | None = None


def get_rag_retriever(repository: TaskRepository) -> RAGRetriever:
    """Get or create RAG retriever instance.
    
    Args:
        repository: Task repository
        
    Returns:
        RAG retriever instance
    """
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = RAGRetriever(repository)
    return _retriever_instance

