"""
Integration Tests - Deadline Parsing with GPT-5 Nano.

Tests that GPT-5 Nano correctly parses relative dates and times
into ISO format.

NOTE: These tests hit the real OpenAI API.
"""

import pytest
from datetime import datetime, timedelta
import os

from src.ai.parsers.task_parser import parse_task_from_transcript


# Skip if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OpenAI API key not available"
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_deadline_parsing_tomorrow():
    """Test parsing 'завтра' (tomorrow)."""

    transcript = "Починить фрезер завтра"
    parsed = await parse_task_from_transcript(transcript, user_id=1)

    # Check deadline was parsed
    assert parsed.deadline is not None, "Deadline should be parsed from 'завтра'"

    # Verify it's tomorrow's date
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    parsed_date = datetime.fromisoformat(parsed.deadline).date()

    assert parsed_date == tomorrow, f"Expected {tomorrow}, got {parsed_date}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_deadline_parsing_tomorrow_with_time():
    """Test parsing 'завтра в 10 утра' (tomorrow at 10 AM)."""

    transcript = "Починить фрезер завтра в 10 утра"
    parsed = await parse_task_from_transcript(transcript, user_id=1)

    # Check deadline was parsed
    assert parsed.deadline is not None, "Deadline should be parsed"

    # Parse the deadline
    deadline_dt = datetime.fromisoformat(parsed.deadline)

    # Verify date is tomorrow
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    assert deadline_dt.date() == tomorrow, f"Expected {tomorrow}, got {deadline_dt.date()}"

    # Verify time is 10:00
    assert deadline_dt.hour == 10, f"Expected hour 10, got {deadline_dt.hour}"
    assert deadline_dt.minute == 0, f"Expected minute 0, got {deadline_dt.minute}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_deadline_parsing_specific_time():
    """Test parsing specific time 'в 15:00' (at 3 PM)."""

    transcript = "Позвонить клиенту сегодня в 15:00"
    parsed = await parse_task_from_transcript(transcript, user_id=1)

    # Check deadline was parsed
    assert parsed.deadline is not None, "Deadline should be parsed"

    # Parse the deadline
    deadline_dt = datetime.fromisoformat(parsed.deadline)

    # Verify time is 15:00
    assert deadline_dt.hour == 15, f"Expected hour 15, got {deadline_dt.hour}"
    assert deadline_dt.minute == 0, f"Expected minute 0, got {deadline_dt.minute}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_deadline_parsing_day_of_week():
    """Test parsing day of week 'в пятницу' (on Friday)."""

    transcript = "Встреча в пятницу в 14:30"
    parsed = await parse_task_from_transcript(transcript, user_id=1)

    # Check deadline was parsed
    assert parsed.deadline is not None, "Deadline should be parsed"

    # Parse the deadline
    deadline_dt = datetime.fromisoformat(parsed.deadline)

    # Verify it's a Friday
    assert deadline_dt.weekday() == 4, f"Expected Friday (4), got {deadline_dt.weekday()}"

    # Verify time is 14:30
    assert deadline_dt.hour == 14, f"Expected hour 14, got {deadline_dt.hour}"
    assert deadline_dt.minute == 30, f"Expected minute 30, got {deadline_dt.minute}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_deadline_parsing_no_deadline():
    """Test that tasks without deadline have None."""

    transcript = "Починить фрезер"
    parsed = await parse_task_from_transcript(transcript, user_id=1)

    # Check deadline is None
    assert parsed.deadline is None, "Deadline should be None when not mentioned"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_deadline_parsing_morning():
    """Test parsing 'утром' (in the morning)."""

    transcript = "Собрать плату завтра утром"
    parsed = await parse_task_from_transcript(transcript, user_id=1)

    # Check deadline was parsed
    assert parsed.deadline is not None, "Deadline should be parsed"

    # Parse the deadline
    deadline_dt = datetime.fromisoformat(parsed.deadline)

    # Verify time is morning (around 9:00)
    assert 8 <= deadline_dt.hour <= 10, f"Expected morning time (8-10), got {deadline_dt.hour}"
