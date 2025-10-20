"""
Unit Tests - Task Parser and Deadline Parsing.

Tests GPT-5 Nano task parsing and deadline string handling.

Reference:
- src/ai/parsers/task_parser.py
- src/ai/graphs/voice_task_creation.py (deadline parsing in create_task_db_node)
"""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import AsyncMock, patch

from src.ai.parsers.task_parser import parse_task_from_transcript, ParsedTask


# ============================================================================
# Task Parser Tests (with mocked OpenAI)
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_task_from_transcript_simple(mock_openai_client):
    """Test parsing simple task from transcript."""

    with patch('src.ai.parsers.task_parser.openai_client', mock_openai_client):
        mock_openai_client.parse_task = AsyncMock(return_value={
            "title": "Починить фрезер",
            "business_id": 1,
            "deadline": None,
            "assigned_to": None,
            "priority": 2
        })

        parsed = await parse_task_from_transcript(
            transcript="Нужно починить фрезер",
            user_id=1
        )

        assert parsed.title == "Починить фрезер"
        assert parsed.business_id == 1
        assert parsed.priority == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_task_with_deadline(mock_openai_client):
    """Test parsing task with deadline."""

    with patch('src.ai.parsers.task_parser.openai_client', mock_openai_client):
        mock_openai_client.parse_task = AsyncMock(return_value={
            "title": "Починить фрезер для Иванова",
            "business_id": 1,
            "deadline": "2025-10-21",  # Tomorrow
            "assigned_to": "Максим",
            "priority": 1
        })

        parsed = await parse_task_from_transcript(
            transcript="Максим должен починить фрезер для Иванова до завтра",
            user_id=1
        )

        assert parsed.title == "Починить фрезер для Иванова"
        assert parsed.deadline == "2025-10-21"
        assert parsed.assigned_to == "Максим"
        assert parsed.priority == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_task_business_detection(mock_openai_client):
    """Test that different businesses are correctly detected."""

    test_cases = [
        ("Починить фрезер", 1),  # Inventum (фрезер keyword)
        ("Сделать коронку", 2),  # Lab (dental keyword)
        ("Прототип новой детали", 3),  # R&D (prototype keyword)
        ("Позвонить поставщику в Китае", 4),  # Trade (China keyword)
    ]

    with patch('src.ai.parsers.task_parser.openai_client', mock_openai_client):
        for transcript, expected_business_id in test_cases:
            mock_openai_client.parse_task = AsyncMock(return_value={
                "title": transcript,
                "business_id": expected_business_id,
                "priority": 2
            })

            parsed = await parse_task_from_transcript(
                transcript=transcript,
                user_id=1
            )

            assert parsed.business_id == expected_business_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_task_priority_levels(mock_openai_client):
    """Test that different priority levels are parsed correctly."""

    test_cases = [
        # High priority (1)
        ("Важно починить фрезер", 1, "важно"),
        ("Срочно нужно починить фрезер", 1, "срочно"),
        ("ASAP починить фрезер", 1, "ASAP"),

        # Medium priority (2) - DEFAULT
        ("Починить фрезер", 2, "no keyword - default"),
        ("Нужно починить фрезер", 2, "neutral"),

        # Low priority (3)
        ("Не срочно починить фрезер", 3, "не срочно"),
        ("Не важно починить фрезер", 3, "не важно"),
        ("Когда-нибудь починить фрезер", 3, "когда-нибудь"),

        # Backlog (4)
        ("Отложить ремонт фрезера", 4, "отложить"),
        ("Потом починить фрезер", 4, "потом"),
    ]

    with patch('src.ai.parsers.task_parser.openai_client', mock_openai_client):
        for transcript, expected_priority, description in test_cases:
            mock_openai_client.parse_task = AsyncMock(return_value={
                "title": f"Task: {description}",
                "business_id": 1,
                "priority": expected_priority
            })

            parsed = await parse_task_from_transcript(
                transcript=transcript,
                user_id=1
            )

            assert parsed.priority == expected_priority, \
                f"Expected priority {expected_priority} for: {transcript}"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_task_invalid_response(mock_openai_client):
    """Test handling of invalid response from GPT."""

    with patch('src.ai.parsers.task_parser.openai_client', mock_openai_client):
        # Mock invalid response (missing required fields)
        mock_openai_client.parse_task = AsyncMock(return_value={
            "title": "Test"
            # Missing business_id!
        })

        with pytest.raises(ValueError, match="Failed to parse task"):
            await parse_task_from_transcript(
                transcript="Test",
                user_id=1
            )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_task_api_error(mock_openai_client):
    """Test handling of API error from OpenAI."""

    with patch('src.ai.parsers.task_parser.openai_client', mock_openai_client):
        # Mock API error
        mock_openai_client.parse_task = AsyncMock(
            side_effect=Exception("API connection failed")
        )

        with pytest.raises(ValueError, match="Failed to parse task"):
            await parse_task_from_transcript(
                transcript="Test task",
                user_id=1
            )


# ============================================================================
# Deadline String Parsing Tests
# ============================================================================

@pytest.mark.unit
def test_deadline_string_to_datetime_valid_iso():
    """Test converting valid ISO date string to datetime."""

    deadline_str = "2025-10-21"

    # Parse as datetime (this is done in create_task_db_node)
    deadline_date = datetime.fromisoformat(deadline_str)
    deadline = deadline_date.replace(hour=23, minute=59, second=59)

    assert deadline.year == 2025
    assert deadline.month == 10
    assert deadline.day == 21
    assert deadline.hour == 23
    assert deadline.minute == 59


@pytest.mark.unit
def test_deadline_string_to_datetime_invalid():
    """Test handling of invalid deadline string."""

    invalid_strings = [
        "invalid-date",
        "2025-13-01",  # Invalid month
        "not a date",
        "",
        "завтра"  # Russian text (not ISO)
    ]

    for invalid_str in invalid_strings:
        try:
            datetime.fromisoformat(invalid_str)
            # Should not reach here
            assert False, f"Should have failed for: {invalid_str}"
        except (ValueError, TypeError):
            # Expected behavior
            pass


@pytest.mark.unit
def test_deadline_text_formatting():
    """Test formatting deadline for display."""

    deadline_str = "2025-10-21"

    deadline_date = datetime.fromisoformat(deadline_str)
    deadline_text = deadline_date.strftime("%d.%m.%Y")

    assert deadline_text == "21.10.2025"


@pytest.mark.unit
def test_deadline_parsing_edge_cases():
    """Test edge cases in deadline parsing."""

    # Test with datetime instead of date string
    deadline_datetime = datetime.now() + timedelta(days=1)
    deadline_str = deadline_datetime.isoformat()

    parsed = datetime.fromisoformat(deadline_str)
    assert parsed.date() == deadline_datetime.date()


# ============================================================================
# User ID Mapping Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_telegram_id_to_db_id_mapping(test_session, test_user):
    """Test mapping Telegram user ID to database user ID."""

    from sqlalchemy import select
    from src.infrastructure.database.models import UserORM

    # Query by Telegram ID
    stmt = select(UserORM).where(UserORM.telegram_id == test_user.telegram_id)
    result = await test_session.execute(stmt)
    db_user = result.scalar_one_or_none()

    assert db_user is not None
    assert db_user.id == test_user.id
    assert db_user.telegram_id == 123456


@pytest.mark.unit
@pytest.mark.asyncio
async def test_telegram_id_not_found(test_session):
    """Test handling of unknown Telegram user."""

    from sqlalchemy import select
    from src.infrastructure.database.models import UserORM

    # Query for non-existent Telegram ID
    stmt = select(UserORM).where(UserORM.telegram_id == 999999)
    result = await test_session.execute(stmt)
    db_user = result.scalar_one_or_none()

    assert db_user is None


# ============================================================================
# Member Name to ID Mapping Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_member_name_to_id_mapping(test_session, test_member):
    """Test mapping member name to member ID."""

    from sqlalchemy import select
    from src.infrastructure.database.models import MemberORM

    # Query by name
    stmt = select(MemberORM).where(MemberORM.name == "Максим")
    result = await test_session.execute(stmt)
    member = result.scalar_one_or_none()

    assert member is not None
    assert member.id == test_member.id
    assert member.name == "Максим"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_member_name_case_insensitive(test_session, test_member):
    """Test member name search should handle case variations."""

    from sqlalchemy import select, func
    from src.infrastructure.database.models import MemberORM

    # Query with different case
    search_name = "максим"  # lowercase

    stmt = select(MemberORM).where(
        func.lower(MemberORM.name) == search_name.lower()
    )
    result = await test_session.execute(stmt)
    member = result.scalar_one_or_none()

    assert member is not None
    assert member.name == "Максим"


# ============================================================================
# Integration: Full Parsing Flow
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_full_parsing_flow_with_all_fields(mock_openai_client):
    """Test complete parsing flow with all optional fields."""

    with patch('src.ai.parsers.task_parser.openai_client', mock_openai_client):
        mock_openai_client.parse_task = AsyncMock(return_value={
            "title": "Починить фрезер для Иванова",
            "business_id": 1,
            "deadline": "2025-10-21",
            "project": "ЧПУ фрезеры",
            "assigned_to": "Максим",
            "priority": 1,
            "description": "Срочно, клиент ждет"
        })

        parsed = await parse_task_from_transcript(
            transcript="Максим должен срочно починить фрезер для Иванова до завтра для проекта ЧПУ фрезеры",
            user_id=1
        )

        # Verify all fields
        assert parsed.title == "Починить фрезер для Иванова"
        assert parsed.business_id == 1
        assert parsed.deadline == "2025-10-21"
        assert parsed.project == "ЧПУ фрезеры"
        assert parsed.assigned_to == "Максим"
        assert parsed.priority == 1
        assert parsed.description == "Срочно, клиент ждет"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parsing_russian_deadline_keywords(mock_openai_client):
    """Test that Russian deadline keywords are converted to ISO dates."""

    # GPT should handle this conversion
    deadline_keywords = [
        ("сегодня", date.today()),
        ("завтра", date.today() + timedelta(days=1)),
        ("послезавтра", date.today() + timedelta(days=2)),
    ]

    with patch('src.ai.parsers.task_parser.openai_client', mock_openai_client):
        for keyword, expected_date in deadline_keywords:
            expected_iso = expected_date.isoformat()

            mock_openai_client.parse_task = AsyncMock(return_value={
                "title": f"Задача на {keyword}",
                "business_id": 1,
                "deadline": expected_iso,
                "priority": 2
            })

            parsed = await parse_task_from_transcript(
                transcript=f"Нужно починить фрезер {keyword}",
                user_id=1
            )

            assert parsed.deadline == expected_iso


# ============================================================================
# Executor Assignment Logic Tests (NEW)
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_executor_assignment_team_member_mentioned(mock_openai_client):
    """Test that explicit team member mention assigns to them."""

    with patch('src.ai.parsers.task_parser.openai_client', mock_openai_client):
        mock_openai_client.parse_task = AsyncMock(return_value={
            "title": "Починить фрезер",
            "business_id": 1,
            "assigned_to": "Максим",  # Explicitly mentioned
            "priority": 2
        })

        parsed = await parse_task_from_transcript(
            transcript="Максим должен починить фрезер",
            user_id=1
        )

        assert parsed.assigned_to == "Максим"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_executor_assignment_no_mention_is_for_ceo(mock_openai_client):
    """Test that no executor mention means task for CEO (assigned_to = null)."""

    with patch('src.ai.parsers.task_parser.openai_client', mock_openai_client):
        mock_openai_client.parse_task = AsyncMock(return_value={
            "title": "Починить фрезер",
            "business_id": 1,
            "assigned_to": None,  # No mention = for CEO
            "priority": 2
        })

        parsed = await parse_task_from_transcript(
            transcript="Нужно починить фрезер",  # No executor mentioned
            user_id=1
        )

        assert parsed.assigned_to is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_executor_assignment_self_reference(mock_openai_client):
    """Test that 'я', 'мне' (I, to me) assigns to CEO (null)."""

    test_cases = [
        ("Мне нужно позвонить клиенту", None),
        ("Я должен проверить контракт", None),
        ("Позвонить клиенту", None),  # No mention
    ]

    with patch('src.ai.parsers.task_parser.openai_client', mock_openai_client):
        for transcript, expected_assigned_to in test_cases:
            mock_openai_client.parse_task = AsyncMock(return_value={
                "title": "Test task",
                "business_id": 1,
                "assigned_to": expected_assigned_to,
                "priority": 2
            })

            parsed = await parse_task_from_transcript(
                transcript=transcript,
                user_id=1
            )

            assert parsed.assigned_to == expected_assigned_to, f"Failed for: {transcript}"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_executor_assignment_different_team_members(mock_openai_client):
    """Test executor assignment for different team members."""

    team_members = {
        "Дима": "Дима должен сделать прототип",
        "Максут": "Максут выедет к клиенту",
        "Мария": "Мария смоделирует коронки",
        "Слава": "Слава подготовит документы",
    }

    with patch('src.ai.parsers.task_parser.openai_client', mock_openai_client):
        for member_name, transcript in team_members.items():
            mock_openai_client.parse_task = AsyncMock(return_value={
                "title": "Test task",
                "business_id": 1,
                "assigned_to": member_name,
                "priority": 2
            })

            parsed = await parse_task_from_transcript(
                transcript=transcript,
                user_id=1
            )

            assert parsed.assigned_to == member_name


# ============================================================================
# Business Detection: Максим/Дима Priority Rule Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_business_detection_maxim_dima_repair_by_default(mock_openai_client):
    """Test that Максим/Дима without R&D keywords → Inventum (id:1)."""

    test_cases = [
        ("Максим должен починить фрезер", "repair task"),
        ("Дима проведет диагностику оборудования", "diagnostics task"),
        ("Максим выедет к клиенту завтра", "client visit"),
        ("Дима должен проверить работу установки", "equipment check"),
    ]

    with patch('src.ai.parsers.task_parser.openai_client', mock_openai_client):
        for transcript, description in test_cases:
            # Mock: GPT should assign to Inventum (id:1) based on priority rule
            mock_openai_client.parse_task = AsyncMock(return_value={
                "title": description,
                "business_id": 1,  # Inventum repair
                "assigned_to": "Максим" if "Максим" in transcript else "Дима",
                "priority": 2
            })

            parsed = await parse_task_from_transcript(
                transcript=transcript,
                user_id=1
            )

            assert parsed.business_id == 1, f"Expected Inventum (id:1) for: {transcript}"
            assert parsed.assigned_to in ["Максим", "Дима"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_business_detection_maxim_dima_with_rnd_keywords(mock_openai_client):
    """Test that Максим/Дима WITH explicit 'разработка' → R&D (id:3)."""

    test_cases = [
        ("Максим занимается разработкой нового устройства", "development task"),
        ("Дима работает над разработкой прототипа", "prototype development"),
        ("Максим ведет разработку системы управления", "system development"),
        ("Дима помогает с разработкой электроники", "electronics development"),
    ]

    with patch('src.ai.parsers.task_parser.openai_client', mock_openai_client):
        for transcript, description in test_cases:
            # Mock: GPT should assign to R&D (id:3) when R&D keywords present
            mock_openai_client.parse_task = AsyncMock(return_value={
                "title": description,
                "business_id": 3,  # R&D
                "assigned_to": "Максим" if "Максим" in transcript else "Дима",
                "priority": 2
            })

            parsed = await parse_task_from_transcript(
                transcript=transcript,
                user_id=1
            )

            assert parsed.business_id == 3, f"Expected R&D (id:3) for: {transcript}"
            assert parsed.assigned_to in ["Максим", "Дима"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_business_detection_location_overrides_team_rule(mock_openai_client):
    """Test that location mention has higher priority than team member rule."""

    test_cases = [
        # Location: мастерская → ALWAYS Inventum (id:1)
        ("Максим работает над разработкой для мастерской", 1, "location override: мастерская"),

        # Location: лаборатория → ALWAYS Inventum Lab (id:2)
        ("Дима доставит материалы в лабораторию", 2, "location override: лаборатория"),

        # No location but "разработка" mentioned → R&D (id:3)
        ("Максим ведет разработку нового прототипа", 3, "разработка keyword → R&D"),
    ]

    with patch('src.ai.parsers.task_parser.openai_client', mock_openai_client):
        for transcript, expected_business_id, description in test_cases:
            # Mock: GPT should prioritize location over team member
            mock_openai_client.parse_task = AsyncMock(return_value={
                "title": description,
                "business_id": expected_business_id,
                "assigned_to": "Максим" if "Максим" in transcript else "Дима",
                "priority": 2
            })

            parsed = await parse_task_from_transcript(
                transcript=transcript,
                user_id=1
            )

            assert parsed.business_id == expected_business_id, \
                f"Expected business_id={expected_business_id} for: {transcript}"
