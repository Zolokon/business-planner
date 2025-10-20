"""
OpenAI API Client - Business Planner.

Client for Whisper, GPT-5 Nano, GPT-5, and Embeddings.

Reference:
- ADR-002 (GPT-5 Nano choice)
- docs/05-ai-specifications/models-config.md
"""

import json
from typing import Any
from openai import AsyncOpenAI

from src.config import settings
from src.utils.logger import logger, log_ai_api_call, mask_sensitive


class OpenAIClient:
    """Client for OpenAI APIs.
    
    Handles:
    - Whisper (voice transcription)
    - GPT-5 Nano (parsing, time estimation)
    - GPT-5 (weekly analytics)
    - text-embedding-3-small (RAG embeddings)
    """
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            organization=settings.openai_org_id
        )
        
        logger.info(
            "openai_client_initialized",
            api_key=mask_sensitive(settings.openai_api_key)
        )
    
    # =========================================================================
    # Voice Transcription (Whisper)
    # =========================================================================
    
    async def transcribe_voice(self, audio_bytes: bytes) -> tuple[str, float]:
        """Transcribe voice message using Whisper.
        
        Args:
            audio_bytes: Audio file bytes (ogg, mp3, wav)
            
        Returns:
            Tuple of (transcript text, confidence)
            
        Raises:
            Exception: If transcription fails
            
        Example:
            >>> transcript, confidence = await client.transcribe_voice(audio)
            >>> print(transcript)
            "Нужно починить фрезер для Иванова"
        """
        import time
        start_time = time.time()
        
        try:
            # Create in-memory file
            from io import BytesIO
            audio_file = BytesIO(audio_bytes)
            audio_file.name = "voice.ogg"
            
            # Call Whisper API
            response = await self.client.audio.transcriptions.create(
                model=settings.model_voice,  # "whisper-1"
                file=audio_file,
                language="ru",  # Russian
                response_format="json"
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log API call
            log_ai_api_call(
                model=settings.model_voice,
                operation="transcribe",
                input_tokens=0,  # Whisper doesn't use tokens
                output_tokens=len(response.text.split()),
                duration_ms=duration_ms,
                cost_usd=0.006 * (len(audio_bytes) / 1024 / 1024 / 60),  # ~$0.006/min
                success=True
            )
            
            # Whisper doesn't return confidence, use 0.95 as default
            confidence = 0.95
            
            return response.text, confidence
            
        except Exception as e:
            logger.error("whisper_transcription_failed", error=str(e))
            raise
    
    # =========================================================================
    # Task Parsing (GPT-5 Nano)
    # =========================================================================
    
    async def parse_task(
        self,
        transcript: str,
        context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Parse task from transcript using GPT-5 Nano.
        
        Args:
            transcript: Voice/text transcript
            context: Additional context (recent tasks, projects, etc.)
            
        Returns:
            Parsed task data (JSON)
            
        Reference: docs/05-ai-specifications/prompts/task-parser.md
        """
        import time
        start_time = time.time()
        
        # Build prompt (from specification)
        system_prompt = self._build_task_parser_system_prompt()
        user_prompt = self._build_task_parser_user_prompt(transcript, context)
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.model_parser,  # "gpt-5-nano"
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
                # Note: GPT-5 nano works best without temperature and max_completion_tokens
            )
            
            duration_ms = int((time.time() - start_time) * 1000)

            # Parse JSON response
            raw_content = response.choices[0].message.content
            logger.debug("gpt_raw_response", content=raw_content[:200])  # First 200 chars
            parsed_data = json.loads(raw_content)
            
            # Log API call
            log_ai_api_call(
                model=settings.model_parser,
                operation="parse_task",
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                duration_ms=duration_ms,
                cost_usd=(response.usage.total_tokens / 1_000_000) * 0.05,  # $0.05/1M
                success=True
            )
            
            return parsed_data
            
        except Exception as e:
            logger.error("task_parsing_failed", error=str(e), transcript=transcript)
            raise
    
    # =========================================================================
    # Time Estimation (GPT-5 Nano with RAG)
    # =========================================================================
    
    async def estimate_time(
        self,
        task_title: str,
        business_name: str,
        similar_tasks: list[dict[str, Any]]
    ) -> int:
        """Estimate task duration using GPT-5 Nano with RAG context.
        
        Args:
            task_title: New task title
            business_name: Business context name
            similar_tasks: List of similar past tasks with actual_duration
            
        Returns:
            Estimated duration in minutes
            
        Reference: docs/05-ai-specifications/prompts/time-estimator.md
        """
        # Build prompt
        if similar_tasks:
            context = self._build_time_estimation_context(
                task_title, business_name, similar_tasks
            )
        else:
            context = self._build_time_estimation_no_history(task_title, business_name)
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.model_reasoning,  # "gpt-5-nano"
                messages=[
                    {
                        "role": "system",
                        "content": "You estimate task duration in minutes based on historical data. Return only the number."
                    },
                    {"role": "user", "content": context}
                ]
                # Note: GPT-5 nano works best without temperature and max_completion_tokens
            )
            
            # Parse duration from response
            duration_text = response.choices[0].message.content.strip()
            duration = int(duration_text)
            
            # Sanity check
            if duration < 1 or duration > 480:
                logger.warning(
                    "unusual_duration_estimate",
                    duration=duration,
                    using_default=True
                )
                return 60  # Default
            
            logger.info(
                "time_estimated",
                task_title=task_title,
                estimated_duration=duration,
                similar_tasks_count=len(similar_tasks)
            )
            
            return duration
            
        except Exception as e:
            logger.error("time_estimation_failed", error=str(e))
            return 60  # Default fallback
    
    # =========================================================================
    # Embeddings (for RAG)
    # =========================================================================
    
    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding vector for text.
        
        Args:
            text: Text to embed (task title)
            
        Returns:
            Embedding vector (1536 dimensions)
            
        Reference: ADR-004 (RAG Strategy)
        """
        try:
            response = await self.client.embeddings.create(
                model=settings.model_embeddings,  # "text-embedding-3-small"
                input=text
            )
            
            embedding = response.data[0].embedding
            
            logger.debug(
                "embedding_generated",
                text_length=len(text),
                embedding_dimensions=len(embedding)
            )
            
            return embedding
            
        except Exception as e:
            logger.error("embedding_generation_failed", error=str(e), text=text[:100])
            raise
    
    # =========================================================================
    # Helper Methods (Prompt Building)
    # =========================================================================
    
    def _build_task_parser_system_prompt(self) -> str:
        """Build system prompt for task parser.

        Reference: docs/05-ai-specifications/prompts/task-parser.md
        """
        return """Parse Russian task from voice/text for CEO managing 4 businesses in Almaty.

BUSINESSES:
1. INVENTUM (id:1) - Dental equipment repair workshop
   Location: "мастерская" (PRIORITY if mentioned!)
   Keywords: фрезер, ремонт, диагностика, сервис, клиент
   Team: Максим, Дима, Максут

2. INVENTUM LAB (id:2) - Dental lab CAD/CAM
   Location: "лаборатория" (PRIORITY if mentioned!)
   Keywords: коронка, моделирование, CAD, CAM, фрезеровка, протез
   Team: Юрий Владимирович, Мария

3. R&D (id:3) - Research & Development (RARE!)
   Keywords: разработка (explicit mention required!)
   Team: Максим, Дима (part-time, rarely)

4. IMPORT & TRADE (id:4) - Equipment import from China
   Keywords: поставщик, Китай, контракт, таможня, импорт, логистика
   Team: Слава

CRITICAL RULES - Business Detection Priority:
1. Location mentioned:
   - "мастерская" → ALWAYS id:1 (Inventum repair)
   - "лаборатория" → ALWAYS id:2 (Inventum Lab)

2. Максим or Дима mentioned (they work mainly in Inventum repair):
   - If "разработка" explicitly mentioned → id:3 (R&D) [RARE CASE]
   - Otherwise → id:1 (Inventum repair) [DEFAULT - most tasks]

3. If no location/team, use keywords to detect business.

RULES:
1. business_id (1-4) - REQUIRED
2. assigned_to: team member name if mentioned, null if "я"/"мне"/not mentioned (CEO task)
   Examples: "Дима починит" → "Дима" | "Починить" → null | "Мне позвонить" → null
3. deadline: ISO format with time if specified
   - Only date: "2025-10-21" (завтра, в пятницу)
   - Date+time: "2025-10-21T14:30:00" (завтра в 14:30, в пятницу утром)
   Examples: "завтра" → "2025-10-21" | "завтра в 15:00" → "2025-10-21T15:00:00"
4. priority (1-4):
   - DEFAULT: 2 (Средний) - use for most tasks
   - If "важно", "срочно", "ASAP" → 1 (Высокий)
   - If "не важно", "не срочно", "когда-нибудь" → 3 (Низкий)
   - If "отложить", "потом" → 4 (Отложенный)
   Examples: "Важно починить" → 1 | "Починить" → 2 | "Не срочно" → 3

JSON OUTPUT:
{"title": "string", "business_id": 1-4, "deadline": "string|null", "project": "string|null", "assigned_to": "name|null", "priority": 1-4}"""
    
    def _build_task_parser_user_prompt(
        self,
        transcript: str,
        context: dict[str, Any] | None
    ) -> str:
        """Build user prompt for task parser."""
        from datetime import datetime

        # Current date/time for relative date parsing
        now = datetime.now()
        current_datetime = now.strftime("%Y-%m-%d %H:%M")
        current_day = now.strftime("%A")  # Monday, Tuesday, etc.

        return f'''Current date/time: {current_datetime} ({current_day})

Parse this task:
"{transcript}"

Extract structured task data in JSON format.
IMPORTANT: Convert relative dates to ISO format using current date above.'''
    
    def _build_time_estimation_context(
        self,
        task_title: str,
        business_name: str,
        similar_tasks: list[dict[str, Any]]
    ) -> str:
        """Build context for time estimation with history."""
        similar_info = []
        for i, task in enumerate(similar_tasks, 1):
            similar_info.append(
                f"{i}. \"{task['title']}\" → actual: {task['actual_duration']} min"
            )
        
        return f"""NEW TASK:
"{task_title}"

Business: {business_name}

SIMILAR PAST TASKS:
{chr(10).join(similar_info)}

Based on these similar tasks, estimate duration in minutes.
Return ONLY a number (minutes)."""
    
    def _build_time_estimation_no_history(
        self,
        task_title: str,
        business_name: str
    ) -> str:
        """Build context for time estimation without history."""
        return f"""NEW TASK:
"{task_title}"

Business: {business_name}

NO SIMILAR TASKS FOUND.

Estimate duration based on task title. Use these guides:
- Phone calls: 30 min
- Repairs: 120 min
- Modeling: 90 min
- Prototypes: 240 min

Return ONLY a number (minutes)."""


# Global client instance
openai_client = OpenAIClient()

