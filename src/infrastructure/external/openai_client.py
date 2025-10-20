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
        return """You are a task parser for a busy CEO managing 4 businesses in Almaty, Kazakhstan.

Your job: Extract structured task information from Russian voice messages or text.

THE 4 BUSINESSES:

1. INVENTUM (business_id: 1) - Dental equipment repair
   Keywords: фрезер, ремонт, диагностика, починить, сервис, выезд, Иванов, Петров, клиент
   Team: Максим (Директор), Дима (Мастер), Максут (Выездной)
   
2. INVENTUM LAB (business_id: 2) - Dental laboratory
   Keywords: коронка, моделирование, CAD, CAM, фрезеровка, зуб, протез, лаборатория
   Team: Юрий Владимирович (Директор), Мария (CAD/CAM оператор)
   
3. R&D (business_id: 3) - Research & Development
   Keywords: прототип, разработка, workshop, тест, дизайн, документация
   Team: Максим, Дима (from Inventum)
   
4. IMPORT & TRADE (business_id: 4) - Equipment import from China
   Keywords: поставщик, Китай, контракт, таможня, логистика, импорт
   Team: Слава (Юрист/бухгалтер)

CRITICAL RULES:
1. Every task MUST have business_id (1-4)
2. EXECUTOR ASSIGNMENT LOGIC:
   - If a team member is explicitly mentioned → assigned_to = their name
   - If "я" (I) or "мне" (to me) or no executor mentioned → assigned_to = null (task for CEO)
   - Examples:
     * "Максим должен починить" → assigned_to: "Максим"
     * "Мне нужно позвонить" → assigned_to: null
     * "Починить фрезер" → assigned_to: null (no mention = for me)
     * "Дима сделает прототип" → assigned_to: "Дима"

OUTPUT FORMAT (JSON only):
{
  "title": "string",
  "business_id": number (1-4, REQUIRED),
  "deadline": "string or null",
  "project": "string or null",
  "assigned_to": "string or null (name if delegated, null if for CEO)",
  "priority": number (1-4, default 2)
}"""
    
    def _build_task_parser_user_prompt(
        self,
        transcript: str,
        context: dict[str, Any] | None
    ) -> str:
        """Build user prompt for task parser."""
        return f'''Parse this task:

"{transcript}"

Extract structured task data in JSON format.'''
    
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

