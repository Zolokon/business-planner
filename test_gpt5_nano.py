#!/usr/bin/env python3
"""
Simple test script to check GPT-5 nano interaction.
Tests different parameter combinations to find what works.
"""

import asyncio
import json
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

async def test_gpt5_nano():
    """Test GPT-5 nano with different configurations."""

    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    test_transcript = "Нужно починить фрезер для Inventum завтра"

    system_prompt = """You are a task parser. Parse the user's message into a JSON object with these fields:
{
  "title": "task title",
  "business_id": 1-4 (1=Inventum, 2=Lab, 3=R&D, 4=Trade),
  "priority": 1-4,
  "deadline_text": "extracted deadline or null"
}"""

    print("=" * 60)
    print("Testing GPT-5 nano configurations")
    print("=" * 60)
    print(f"\nTranscript: {test_transcript}")
    print(f"\nModel: gpt-5-nano")

    # Test 1: Minimal parameters
    print("\n--- Test 1: Minimal parameters ---")
    try:
        response = await client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": test_transcript}
            ]
        )
        print(f"✅ Success!")
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 2: With response_format
    print("\n--- Test 2: With response_format=json_object ---")
    try:
        response = await client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": test_transcript}
            ],
            response_format={"type": "json_object"}
        )
        print(f"✅ Success!")
        print(f"Response: {response.choices[0].message.content}")
        # Try to parse as JSON
        parsed = json.loads(response.choices[0].message.content)
        print(f"Parsed JSON: {json.dumps(parsed, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 3: With max_completion_tokens
    print("\n--- Test 3: With max_completion_tokens ---")
    try:
        response = await client.chat.completions.create(
            model="gpt-5-nano",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": test_transcript}
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=500
        )
        print(f"✅ Success!")
        print(f"Response: {response.choices[0].message.content}")
        parsed = json.loads(response.choices[0].message.content)
        print(f"Parsed JSON: {json.dumps(parsed, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 4: Check available parameters
    print("\n--- Test 4: Model info ---")
    try:
        # List models
        models = await client.models.list()
        gpt5_models = [m for m in models.data if 'gpt-5' in m.id.lower()]
        print(f"Available GPT-5 models: {[m.id for m in gpt5_models]}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    asyncio.run(test_gpt5_nano())
