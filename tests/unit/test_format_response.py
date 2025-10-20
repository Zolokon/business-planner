"""
Unit Tests - format_response_node (Voice Task Creation).

Tests message formatting logic for Telegram responses.

Reference: src/ai/graphs/voice_task_creation.py (format_response_node)
"""

import pytest
from datetime import datetime

from src.ai.graphs.voice_task_creation import format_response_node, VoiceTaskState


# ============================================================================
# Success Cases
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_format_response_success_minimal():
    """Test formatting successful response with minimal data."""

    state: VoiceTaskState = {
        "audio_bytes": b"",
        "audio_duration": 10,
        "user_id": 1,
        "telegram_chat_id": 123456,
        "transcript": "Починить фрезер",
        "transcript_confidence": 0.95,
        "parsed_title": "Починить фрезер",
        "parsed_business_id": 1,
        "parsed_deadline_text": None,
        "parsed_assigned_to": None,
        "parsed_priority": 2,
        "similar_tasks_count": 0,
        "estimated_duration": None,
        "created_task_id": 1,
        "telegram_response": None,
        "error": None,
        "error_message": None,
        "processing_start": datetime.now(),
        "processing_time_ms": 0
    }

    result = await format_response_node(state)

    # Check response exists (transcript now sent separately)
    assert result["telegram_response"] is not None
    assert "ЗАДАЧА СОЗДАНА" in result["telegram_response"]
    assert "Починить фрезер" in result["telegram_response"]  # Task title
    assert "Inventum" in result["telegram_response"]  # Business name
    assert "СРЕДНИЙ" in result["telegram_response"]  # Priority
    assert "Дедлайн:" in result["telegram_response"]  # Always shown
    assert "не указан" in result["telegram_response"]  # No deadline set
    # Transcript should be in state (sent separately by handler)
    assert result.get("transcript") == "Починить фрезер"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_format_response_success_full_data():
    """Test formatting with all optional fields present."""

    state: VoiceTaskState = {
        "audio_bytes": b"",
        "audio_duration": 10,
        "user_id": 1,
        "telegram_chat_id": 123456,
        "transcript": "Починить фрезер для Иванова до завтра",
        "transcript_confidence": 0.95,
        "parsed_title": "Починить фрезер для Иванова",
        "parsed_business_id": 1,
        "parsed_deadline": "2025-10-21",  # ISO format
        "parsed_assigned_to": "Максим",
        "parsed_priority": 1,  # HIGH
        "similar_tasks_count": 5,
        "estimated_duration": 120,  # 2 hours
        "created_task_id": 1,
        "telegram_response": None,
        "error": None,
        "error_message": None,
        "processing_start": datetime.now(),
        "processing_time_ms": 0
    }

    result = await format_response_node(state)

    response = result["telegram_response"]

    # Check all fields present (transcript now sent separately)
    assert "ЗАДАЧА СОЗДАНА" in response
    assert "Починить фрезер для Иванова" in response  # Task title
    assert "Inventum" in response
    assert "ВЫСОКИЙ" in response  # Priority
    assert "21.10.2025" in response  # Deadline formatted
    assert "Максим" in response  # Assigned to
    assert "2 ч" in response  # Time estimation
    assert "высокая точность" in response  # Confidence (>= 3 similar tasks)
    # Transcript should be in state (sent separately by handler)
    assert result.get("transcript") == "Починить фрезер для Иванова до завтра"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_format_response_business_names():
    """Test all business names are correctly mapped."""

    businesses = {
        1: "Inventum",
        2: "Inventum Lab",
        3: "R&D",
        4: "Trade",
        99: "Business 99"  # Unknown business
    }

    for business_id, expected_name in businesses.items():
        state: VoiceTaskState = {
            "audio_bytes": b"",
            "audio_duration": 10,
            "user_id": 1,
            "telegram_chat_id": 123456,
            "transcript": "Test",
            "transcript_confidence": 0.95,
            "parsed_title": "Test task",
            "parsed_business_id": business_id,
            "parsed_deadline_text": None,
            "parsed_assigned_to": None,
            "parsed_priority": 2,
            "similar_tasks_count": 0,
            "estimated_duration": None,
            "created_task_id": 1,
            "telegram_response": None,
            "error": None,
            "error_message": None,
            "processing_start": datetime.now(),
            "processing_time_ms": 0
        }

        result = await format_response_node(state)
        assert expected_name in result["telegram_response"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_format_response_priority_levels():
    """Test all priority levels are correctly formatted."""

    priorities = {
        1: "ВЫСОКИЙ",
        2: "СРЕДНИЙ",
        3: "НИЗКИЙ",
        4: "ОТЛОЖЕННЫЙ"
    }

    for priority, expected_text in priorities.items():
        state: VoiceTaskState = {
            "audio_bytes": b"",
            "audio_duration": 10,
            "user_id": 1,
            "telegram_chat_id": 123456,
            "transcript": "Test",
            "transcript_confidence": 0.95,
            "parsed_title": "Test task",
            "parsed_business_id": 1,
            "parsed_deadline_text": None,
            "parsed_assigned_to": None,
            "parsed_priority": priority,
            "similar_tasks_count": 0,
            "estimated_duration": None,
            "created_task_id": 1,
            "telegram_response": None,
            "error": None,
            "error_message": None,
            "processing_start": datetime.now(),
            "processing_time_ms": 0
        }

        result = await format_response_node(state)
        assert expected_text in result["telegram_response"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_format_response_time_estimation_formats():
    """Test time estimation is formatted correctly (hours, minutes, both)."""

    test_cases = [
        (30, "30 мин"),  # Minutes only
        (60, "1 ч"),  # 1 hour
        (120, "2 ч"),  # 2 hours
        (90, "1 ч 30 мин"),  # Hours and minutes
        (135, "2 ч 15 мин")  # Hours and minutes
    ]

    for duration_mins, expected_format in test_cases:
        state: VoiceTaskState = {
            "audio_bytes": b"",
            "audio_duration": 10,
            "user_id": 1,
            "telegram_chat_id": 123456,
            "transcript": "Test",
            "transcript_confidence": 0.95,
            "parsed_title": "Test task",
            "parsed_business_id": 1,
            "parsed_deadline_text": None,
            "parsed_assigned_to": None,
            "parsed_priority": 2,
            "similar_tasks_count": 0,
            "estimated_duration": duration_mins,
            "created_task_id": 1,
            "telegram_response": None,
            "error": None,
            "error_message": None,
            "processing_start": datetime.now(),
            "processing_time_ms": 0
        }

        result = await format_response_node(state)
        assert expected_format in result["telegram_response"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_format_response_estimation_confidence():
    """Test estimation confidence varies based on similar tasks count."""

    # Low confidence (< 3 similar tasks)
    state_low: VoiceTaskState = {
        "audio_bytes": b"",
        "audio_duration": 10,
        "user_id": 1,
        "telegram_chat_id": 123456,
        "transcript": "Test",
        "transcript_confidence": 0.95,
        "parsed_title": "Test task",
        "parsed_business_id": 1,
        "parsed_deadline_text": None,
        "parsed_assigned_to": None,
        "parsed_priority": 2,
        "similar_tasks_count": 2,
        "estimated_duration": 60,
        "created_task_id": 1,
        "telegram_response": None,
        "error": None,
        "error_message": None,
        "processing_start": datetime.now(),
        "processing_time_ms": 0
    }

    result_low = await format_response_node(state_low)
    assert "(оценка)" in result_low["telegram_response"]

    # High confidence (>= 3 similar tasks)
    state_high = {**state_low, "similar_tasks_count": 5}
    result_high = await format_response_node(state_high)
    assert "(высокая точность)" in result_high["telegram_response"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_format_response_no_emojis():
    """Test that response does NOT contain emojis (clean formatting)."""

    state: VoiceTaskState = {
        "audio_bytes": b"",
        "audio_duration": 10,
        "user_id": 1,
        "telegram_chat_id": 123456,
        "transcript": "Test",
        "transcript_confidence": 0.95,
        "parsed_title": "Test task",
        "parsed_business_id": 1,
        "parsed_deadline": "2025-10-21",
        "parsed_assigned_to": "Максим",
        "parsed_priority": 1,
        "similar_tasks_count": 5,
        "estimated_duration": 120,
        "created_task_id": 1,
        "telegram_response": None,
        "error": None,
        "error_message": None,
        "processing_start": datetime.now(),
        "processing_time_ms": 0
    }

    result = await format_response_node(state)
    response = result["telegram_response"]

    # Check no emojis (common ones)
    forbidden_emojis = ["✅", "📋", "🎯", "⏱️", "📅", "👤"]
    for emoji in forbidden_emojis:
        assert emoji not in response


# ============================================================================
# Error Cases
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_format_response_transcription_failed():
    """Test error formatting for transcription failure."""

    state: VoiceTaskState = {
        "audio_bytes": b"",
        "audio_duration": 10,
        "user_id": 1,
        "telegram_chat_id": 123456,
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
        "error": "TranscriptionFailed",
        "error_message": "API error",
        "processing_start": datetime.now(),
        "processing_time_ms": 0
    }

    result = await format_response_node(state)

    assert "[ОШИБКА]" in result["telegram_response"]
    assert "не удалось распознать голос" in result["telegram_response"].lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_format_response_parsing_failed():
    """Test error formatting for task parsing failure."""

    state: VoiceTaskState = {
        "audio_bytes": b"",
        "audio_duration": 10,
        "user_id": 1,
        "telegram_chat_id": 123456,
        "transcript": "Test",
        "transcript_confidence": 0.95,
        "parsed_title": None,
        "parsed_business_id": None,
        "parsed_deadline_text": None,
        "parsed_assigned_to": None,
        "parsed_priority": None,
        "similar_tasks_count": 0,
        "estimated_duration": None,
        "created_task_id": None,
        "telegram_response": None,
        "error": "ParsingFailed",
        "error_message": "Could not understand task",
        "processing_start": datetime.now(),
        "processing_time_ms": 0
    }

    result = await format_response_node(state)

    assert "[ОШИБКА]" in result["telegram_response"]
    assert "не удалось понять задачу" in result["telegram_response"].lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_format_response_task_creation_failed():
    """Test error formatting for database task creation failure."""

    state: VoiceTaskState = {
        "audio_bytes": b"",
        "audio_duration": 10,
        "user_id": 1,
        "telegram_chat_id": 123456,
        "transcript": "Test",
        "transcript_confidence": 0.95,
        "parsed_title": "Test task",
        "parsed_business_id": 1,
        "parsed_deadline_text": None,
        "parsed_assigned_to": None,
        "parsed_priority": 2,
        "similar_tasks_count": 0,
        "estimated_duration": 60,
        "created_task_id": None,
        "telegram_response": None,
        "error": "TaskCreationFailed",
        "error_message": "Database connection lost",
        "processing_start": datetime.now(),
        "processing_time_ms": 0
    }

    result = await format_response_node(state)

    assert "[ОШИБКА]" in result["telegram_response"]
    assert "ошибка при создании задачи" in result["telegram_response"].lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_format_response_unknown_error():
    """Test formatting for unknown error types."""

    state: VoiceTaskState = {
        "audio_bytes": b"",
        "audio_duration": 10,
        "user_id": 1,
        "telegram_chat_id": 123456,
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
        "error": "UnknownError",
        "error_message": "Something went wrong",
        "processing_start": datetime.now(),
        "processing_time_ms": 0
    }

    result = await format_response_node(state)

    assert "[ОШИБКА]" in result["telegram_response"]
    assert "Something went wrong" in result["telegram_response"]


# ============================================================================
# Edge Cases
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_format_response_invalid_deadline_format():
    """Test handling of invalid deadline format (graceful degradation)."""

    state: VoiceTaskState = {
        "audio_bytes": b"",
        "audio_duration": 10,
        "user_id": 1,
        "telegram_chat_id": 123456,
        "transcript": "Test",
        "transcript_confidence": 0.95,
        "parsed_title": "Test task",
        "parsed_business_id": 1,
        "parsed_deadline": "invalid-date",  # Invalid format
        "parsed_assigned_to": None,
        "parsed_priority": 2,
        "similar_tasks_count": 0,
        "estimated_duration": None,
        "created_task_id": 1,
        "telegram_response": None,
        "error": None,
        "error_message": None,
        "processing_start": datetime.now(),
        "processing_time_ms": 0
    }

    result = await format_response_node(state)

    # Should not crash, show error message for invalid format
    assert "ЗАДАЧА СОЗДАНА" in result["telegram_response"]
    assert "Дедлайн:" in result["telegram_response"]
    assert "ошибка формата" in result["telegram_response"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_format_response_deadline_with_time():
    """Test deadline formatting with time component."""

    # Test date + time
    state_with_time: VoiceTaskState = {
        "audio_bytes": b"",
        "audio_duration": 10,
        "user_id": 1,
        "telegram_chat_id": 123456,
        "transcript": "Test",
        "transcript_confidence": 0.95,
        "parsed_title": "Test task",
        "parsed_business_id": 1,
        "parsed_deadline": "2025-10-21T14:30:00",  # With time
        "parsed_assigned_to": None,
        "parsed_priority": 2,
        "similar_tasks_count": 0,
        "estimated_duration": None,
        "created_task_id": 1,
        "telegram_response": None,
        "error": None,
        "error_message": None,
        "processing_start": datetime.now(),
        "processing_time_ms": 0
    }

    result = await format_response_node(state_with_time)
    assert "21.10.2025 в 14:30" in result["telegram_response"]

    # Test date only (no time)
    state_date_only: VoiceTaskState = {
        "audio_bytes": b"",
        "audio_duration": 10,
        "user_id": 1,
        "telegram_chat_id": 123456,
        "transcript": "Test",
        "transcript_confidence": 0.95,
        "parsed_title": "Test task",
        "parsed_business_id": 1,
        "parsed_deadline": "2025-10-21",  # No time
        "parsed_assigned_to": None,
        "parsed_priority": 2,
        "similar_tasks_count": 0,
        "estimated_duration": None,
        "created_task_id": 1,
        "telegram_response": None,
        "error": None,
        "error_message": None,
        "processing_start": datetime.now(),
        "processing_time_ms": 0
    }

    result = await format_response_node(state_date_only)
    assert "21.10.2025" in result["telegram_response"]
    assert "в 00:00" not in result["telegram_response"]  # Should not show midnight


@pytest.mark.unit
@pytest.mark.asyncio
async def test_format_response_processing_time_calculated():
    """Test that processing time is calculated correctly."""

    start_time = datetime.now()

    state: VoiceTaskState = {
        "audio_bytes": b"",
        "audio_duration": 10,
        "user_id": 1,
        "telegram_chat_id": 123456,
        "transcript": "Test",
        "transcript_confidence": 0.95,
        "parsed_title": "Test task",
        "parsed_business_id": 1,
        "parsed_deadline_text": None,
        "parsed_assigned_to": None,
        "parsed_priority": 2,
        "similar_tasks_count": 0,
        "estimated_duration": None,
        "created_task_id": 1,
        "telegram_response": None,
        "error": None,
        "error_message": None,
        "processing_start": start_time,
        "processing_time_ms": 0
    }

    result = await format_response_node(state)

    # Check processing time was set
    assert result["processing_time_ms"] > 0
    assert isinstance(result["processing_time_ms"], int)
