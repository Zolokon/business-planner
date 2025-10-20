"""
Voice Task Creation Workflow - Business Planner.

LangGraph workflow: Voice message → Structured task.

Reference:
- ADR-001 (LangGraph)
- docs/05-ai-specifications/langgraph-flows.md
"""

from typing import TypedDict
from datetime import datetime

from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.external.openai_client import openai_client
from src.ai.parsers.task_parser import parse_task_from_transcript
from src.ai.rag.retriever import RAGRetriever
from src.ai.rag.embeddings import generate_and_store_embedding
from src.infrastructure.database.repositories.task_repository import TaskRepository
from src.domain.models import TaskCreate, Task
from src.utils.logger import logger


# ============================================================================
# State Definition
# ============================================================================

class VoiceTaskState(TypedDict):
    """State for voice task creation workflow.
    
    Reference: docs/05-ai-specifications/langgraph-flows.md
    """
    
    # Input
    audio_bytes: bytes
    audio_duration: int  # seconds
    user_id: int
    telegram_chat_id: int
    
    # Processing
    transcript: str | None
    transcript_confidence: float | None
    
    parsed_title: str | None
    parsed_business_id: int | None
    parsed_deadline_text: str | None
    parsed_assigned_to: str | None
    parsed_priority: int | None
    
    similar_tasks_count: int
    estimated_duration: int | None
    
    # Output
    created_task_id: int | None
    telegram_response: str | None
    
    # Errors
    error: str | None
    error_message: str | None
    
    # Metadata
    processing_start: datetime
    processing_time_ms: int


# ============================================================================
# Workflow Nodes
# ============================================================================

async def transcribe_voice_node(state: VoiceTaskState) -> VoiceTaskState:
    """Node 1: Transcribe voice using Whisper API.
    
    Reference: docs/05-ai-specifications/langgraph-flows.md (Node 1)
    """
    
    logger.info("node_transcribe_start", audio_duration=state["audio_duration"])
    
    try:
        transcript, confidence = await openai_client.transcribe_voice(
            state["audio_bytes"]
        )
        
        logger.info(
            "node_transcribe_complete",
            transcript=transcript,
            confidence=confidence
        )
        
        return {
            **state,
            "transcript": transcript,
            "transcript_confidence": confidence
        }
        
    except Exception as e:
        logger.error("node_transcribe_failed", error=str(e))
        return {
            **state,
            "error": "TranscriptionFailed",
            "error_message": f"Не удалось распознать голос: {str(e)}"
        }


async def parse_task_node(
    state: VoiceTaskState
) -> VoiceTaskState:
    """Node 2: Parse task structure using GPT-5 Nano.

    Reference: docs/05-ai-specifications/langgraph-flows.md (Node 2)
    """
    
    if state.get("error"):
        return state  # Skip if previous error
    
    logger.info("node_parse_start", transcript=state["transcript"])
    
    try:
        # Parse with GPT-5 Nano
        parsed = await parse_task_from_transcript(
            transcript=state["transcript"],
            user_id=state["user_id"]
        )
        
        logger.info(
            "node_parse_complete",
            title=parsed.title,
            business_id=parsed.business_id,
            deadline=parsed.deadline
        )

        return {
            **state,
            "parsed_title": parsed.title,
            "parsed_business_id": parsed.business_id,
            "parsed_deadline": parsed.deadline,  # Date string
            "parsed_assigned_to": parsed.assigned_to,
            "parsed_priority": parsed.priority
        }
        
    except Exception as e:
        logger.error("node_parse_failed", error=str(e))
        return {
            **state,
            "error": "ParsingFailed",
            "error_message": f"Не удалось понять задачу: {str(e)}"
        }


async def estimate_time_rag_node(
    state: VoiceTaskState
) -> VoiceTaskState:
    """Node 3: Estimate time using RAG.

    Reference:
    - ADR-004 (RAG Strategy)
    - docs/05-ai-specifications/langgraph-flows.md (Node 3)
    """

    if state.get("error"):
        return state

    logger.info(
        "node_estimate_start",
        title=state["parsed_title"],
        business_id=state["parsed_business_id"]
    )

    try:
        # Get database session
        from src.infrastructure.database import get_session
        session_gen = get_session()
        session = await anext(session_gen)

        try:
            # Get repository
            repo = TaskRepository(session)
            retriever = RAGRetriever(repo)
        
            # Find similar tasks (with business isolation!)
            similar_tasks = await retriever.find_similar_tasks(
                task_title=state["parsed_title"],
                business_id=state["parsed_business_id"]
            )

            # Estimate time
            if similar_tasks:
                # Format for GPT-5 Nano
                similar_data = [
                    {
                        "title": t.title,
                        "actual_duration": t.actual_duration
                    }
                    for t in similar_tasks
                ]

                estimated_duration = await openai_client.estimate_time(
                    task_title=state["parsed_title"],
                    business_name=f"Business {state['parsed_business_id']}",
                    similar_tasks=similar_data
                )
            else:
                # No history, use default
                estimated_duration = 60  # 1 hour default

            logger.info(
                "node_estimate_complete",
                estimated_duration=estimated_duration,
                similar_tasks_count=len(similar_tasks)
            )

            return {
                **state,
                "similar_tasks_count": len(similar_tasks),
                "estimated_duration": estimated_duration
            }
        finally:
            await session.close()

    except Exception as e:
        logger.warning("node_estimate_failed", error=str(e), using_default=True)
        # Non-critical error, use default
        return {
            **state,
            "similar_tasks_count": 0,
            "estimated_duration": 60
        }


async def create_task_db_node(
    state: VoiceTaskState
) -> VoiceTaskState:
    """Node 4: Create task in database.

    Reference: docs/05-ai-specifications/langgraph-flows.md (Node 5)
    """

    if state.get("error"):
        return state

    logger.info("node_create_task_start")

    try:
        # Get database session
        from src.infrastructure.database import get_session
        from datetime import datetime
        session_gen = get_session()
        session = await anext(session_gen)

        try:
            # Create task
            repo = TaskRepository(session)

            # Convert deadline string to datetime if present
            deadline = None
            deadline_text = None
            if state.get("parsed_deadline"):
                try:
                    # Parse date string (e.g. "2025-10-20")
                    deadline_date = datetime.fromisoformat(state["parsed_deadline"])
                    # Set time to end of day
                    deadline = deadline_date.replace(hour=23, minute=59, second=59)
                    deadline_text = deadline_date.strftime("%d.%m.%Y")
                except (ValueError, TypeError) as e:
                    logger.warning("deadline_parse_failed", deadline=state.get("parsed_deadline"), error=str(e))

            task_data = TaskCreate(
                title=state["parsed_title"],
                business_id=state["parsed_business_id"],
                priority=state.get("parsed_priority", 2),
                estimated_duration=state.get("estimated_duration"),
                deadline=deadline,
                deadline_text=deadline_text,
                created_via="voice"
            )

            task = await repo.create(task_data, user_id=state["user_id"])

            # Generate embedding (async, doesn't block)
            # This will happen in background
            # await generate_and_store_embedding(task.id, task.title, repo)

            logger.info(
                "node_create_task_complete",
                task_id=task.id,
                business_id=task.business_id
            )

            return {
                **state,
                "created_task_id": task.id
            }
        finally:
            await session.close()

    except Exception as e:
        logger.error("node_create_task_failed", error=str(e))
        return {
            **state,
            "error": "TaskCreationFailed",
            "error_message": f"Не удалось создать задачу: {str(e)}"
        }


async def format_response_node(
    state: VoiceTaskState
) -> VoiceTaskState:
    """Node 5: Format Telegram response.

    Reference: docs/05-ai-specifications/langgraph-flows.md (Node 7)
    """

    # If error, format error message
    if state.get("error"):
        error_messages = {
            "TranscriptionFailed": "🎤 Не удалось распознать голос. Попробуйте еще раз.",
            "ParsingFailed": "❌ Не удалось понять задачу. Уточните, пожалуйста.",
            "TaskCreationFailed": "❌ Ошибка при создании задачи. Попробуйте позже."
        }

        message = error_messages.get(
            state["error"],
            f"❌ Произошла ошибка: {state.get('error_message', 'Неизвестная ошибка')}"
        )

        return {**state, "telegram_response": message}

    # Success message - get business name from database
    business_emoji = {1: "🔧", 2: "🦷", 3: "🔬", 4: "💼"}
    business_names = {1: "Inventum", 2: "Inventum Lab", 3: "R&D", 4: "Trade"}

    business_name = business_names.get(state['parsed_business_id'], f"Business {state['parsed_business_id']}")

    message = f"""✅ Создал задачу:

{state['parsed_title']}

{business_emoji.get(state['parsed_business_id'], '📋')} Бизнес: {business_name}
"""
    
    if state.get("parsed_assigned_to"):
        message += f"👤 Кому: {state['parsed_assigned_to']}\n"

    if state.get("parsed_deadline"):
        # Convert deadline string to readable format
        from datetime import datetime
        try:
            deadline_date = datetime.fromisoformat(state["parsed_deadline"])
            deadline_text = deadline_date.strftime("%d.%m.%Y")
            message += f"📅 {deadline_text}\n"
        except (ValueError, TypeError):
            pass
    
    if state.get("estimated_duration"):
        hours = state["estimated_duration"] // 60
        mins = state["estimated_duration"] % 60
        
        if hours > 0:
            time_str = f"{hours} ч {mins} мин" if mins > 0 else f"{hours} ч"
        else:
            time_str = f"{mins} мин"
        
        confidence_emoji = "🎯" if state["similar_tasks_count"] >= 3 else "📊"
        message += f"⏱️ {confidence_emoji} ~{time_str}"
        
        if state["similar_tasks_count"] > 0:
            message += f" (на основе {state['similar_tasks_count']} похожих задач)"
    
    # Calculate processing time
    processing_time = int((datetime.now() - state["processing_start"]).total_seconds() * 1000)
    
    return {
        **state,
        "telegram_response": message,
        "processing_time_ms": processing_time
    }


# ============================================================================
# Graph Definition
# ============================================================================

def create_voice_task_graph():
    """Create voice-to-task LangGraph workflow.
    
    Workflow:
    1. Transcribe voice (Whisper)
    2. Parse task (GPT-5 Nano)
    3. Estimate time (RAG + GPT-5 Nano)
    4. Create task in DB
    5. Format response
    
    Returns:
        Compiled LangGraph application
        
    Reference: ADR-001 (LangGraph decision)
    """
    
    # Create graph
    graph = StateGraph(VoiceTaskState)
    
    # Add nodes
    graph.add_node("transcribe", transcribe_voice_node)
    graph.add_node("parse", parse_task_node)
    graph.add_node("estimate_time", estimate_time_rag_node)
    graph.add_node("create_task", create_task_db_node)
    graph.add_node("format_response", format_response_node)
    
    # Define edges (linear flow)
    graph.add_edge("transcribe", "parse")
    graph.add_edge("parse", "estimate_time")
    graph.add_edge("estimate_time", "create_task")
    graph.add_edge("create_task", "format_response")
    graph.add_edge("format_response", END)
    
    # Set entry point
    graph.set_entry_point("transcribe")
    
    # Compile (with checkpointing for production)
    # TODO: Add PostgresCheckpointer in production
    app = graph.compile()
    
    logger.info("voice_task_graph_created")
    
    return app


# Global graph instance
voice_task_graph = create_voice_task_graph()


# ============================================================================
# Helper Function
# ============================================================================

async def process_voice_message(
    audio_bytes: bytes,
    audio_duration: int,
    user_id: int,
    telegram_chat_id: int,
    session: AsyncSession
) -> dict:
    """Process voice message through LangGraph workflow.
    
    Args:
        audio_bytes: Voice message audio
        audio_duration: Duration in seconds
        user_id: User ID
        telegram_chat_id: Telegram chat ID
        session: Database session
        
    Returns:
        Result dict with task_id and telegram_response
        
    Example:
        >>> result = await process_voice_message(
        ...     audio_bytes=audio,
        ...     audio_duration=15,
        ...     user_id=1,
        ...     telegram_chat_id=123456,
        ...     session=session
        ... )
        >>> print(result["telegram_response"])
        "✅ Создал задачу: Починить фрезер..."
    """
    
    logger.info(
        "voice_processing_start",
        user_id=user_id,
        audio_duration=audio_duration
    )
    
    # Initialize state
    initial_state: VoiceTaskState = {
        "audio_bytes": audio_bytes,
        "audio_duration": audio_duration,
        "user_id": user_id,
        "telegram_chat_id": telegram_chat_id,
        "transcript": None,
        "transcript_confidence": None,
        "parsed_title": None,
        "parsed_business_id": None,
        "parsed_deadline_text": None,
        "parsed_assigned_to": None,
        "parsed_priority": None,
        "similar_tasks_count": 0,
        "estimated_duration": None,
        "created_task_id": None,
        "telegram_response": None,
        "error": None,
        "error_message": None,
        "processing_start": datetime.now(),
        "processing_time_ms": 0
    }
    
    # Run workflow
    # Note: Pass session to nodes that need it
    # TODO: Implement proper session injection
    result = await voice_task_graph.ainvoke(initial_state)
    
    logger.info(
        "voice_processing_complete",
        user_id=user_id,
        task_id=result.get("created_task_id"),
        processing_time_ms=result.get("processing_time_ms"),
        success=result.get("error") is None
    )
    
    return result

