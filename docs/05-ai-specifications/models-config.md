# AI Models Configuration - Business Planner

> **Complete AI models setup and configuration**  
> **Created**: 2025-10-17  
> **Reference**: ADR-002 (GPT-5 Nano Choice)

---

## 🎯 AI Architecture Summary

### Three-Tier Strategy

```
Tier 1: Ultra-Fast Parsing (90% of calls)
  → GPT-5 Nano ($0.05/1M tokens)
  
Tier 2: Smart Logic (8% of calls)
  → GPT-5 Nano ($0.05/1M tokens)
  
Tier 3: Deep Analytics (2% of calls)
  → GPT-5 (premium)
```

---

## 📋 Model Registry

### Core Models

```python
from enum import Enum

class AIModel(str, Enum):
    """AI models used in Business Planner."""
    
    # Voice
    WHISPER = "whisper-1"
    
    # Tier 1 & 2: Fast & Cheap
    GPT_5_NANO = "gpt-5-nano"
    
    # Tier 3: Premium Analytics
    GPT_5 = "gpt-5"
    
    # Embeddings
    EMBEDDING_SMALL = "text-embedding-3-small"


# Model assignments by operation
MODEL_ASSIGNMENTS = {
    # Voice processing
    "voice_transcription": AIModel.WHISPER,
    
    # Task parsing (Tier 1)
    "task_parser": AIModel.GPT_5_NANO,
    "business_detector": AIModel.GPT_5_NANO,
    "deadline_parser": AIModel.GPT_5_NANO,
    
    # Smart logic (Tier 2)
    "time_estimator": AIModel.GPT_5_NANO,
    "priority_calculator": AIModel.GPT_5_NANO,
    "daily_optimizer": AIModel.GPT_5_NANO,
    
    # Premium analytics (Tier 3)
    "weekly_analytics": AIModel.GPT_5,
    "pattern_analysis": AIModel.GPT_5,
    "strategic_recommendations": AIModel.GPT_5,
    
    # Embeddings
    "task_embeddings": AIModel.EMBEDDING_SMALL
}
```

---

## ⚙️ Model Configurations

### 1. Whisper (Voice Transcription)

```python
WHISPER_CONFIG = {
    "model": "whisper-1",
    "language": "ru",  # Russian
    "response_format": "json",
    "temperature": 0.0,  # Most accurate transcription
    "timeout": 30.0
}

# Pricing
WHISPER_PRICING = {
    "cost_per_minute": 0.006,  # $0.006 per minute
    "expected_usage": 500,  # messages/month
    "avg_duration": 30,  # seconds
    "monthly_cost": 0.006 * (500 * 30 / 60)  # ~$1.50/month
}
```

---

### 2. GPT-5 Nano (Tier 1 & 2)

```python
GPT_5_NANO_CONFIG = {
    "model": "gpt-5-nano",
    "temperature": {
        "parsing": 0.1,      # Low for consistency
        "estimation": 0.3,   # Slightly higher
        "general": 0.2       # Default
    },
    "max_tokens": {
        "parsing": 500,      # Structured output
        "estimation": 10,    # Just a number
        "general": 1000      # Default
    },
    "response_format": "json_object",  # For structured outputs
    "timeout": 5.0,
    "retry": {
        "max_attempts": 3,
        "exponential_backoff": True
    }
}

# Pricing
GPT_5_NANO_PRICING = {
    "cost_per_1m_tokens": 0.05,  # $0.05 / 1M
    "expected_usage": {
        "parsing": 500 * 700,      # 500 tasks × 700 tokens = 350K
        "estimation": 500 * 2000,  # 500 tasks × 2K tokens = 1M
        "total_tokens": 1_350_000  # 1.35M tokens/month
    },
    "monthly_cost": 1.35 * 0.05  # ~$0.07/month ✨
}
```

---

### 3. GPT-5 (Tier 3 - Premium)

```python
GPT_5_CONFIG = {
    "model": "gpt-5",
    "temperature": 0.7,  # Creative for insights
    "max_tokens": 2000,  # Detailed analysis
    "timeout": 30.0,
    "frequency_penalty": 0.1,  # Reduce repetition
    "presence_penalty": 0.1
}

# Pricing
GPT_5_PRICING = {
    "frequency": 4,  # Weekly = 4 times/month
    "tokens_per_run": 52_000,  # 50K input + 2K output
    "total_tokens_month": 208_000,
    "monthly_cost": 2.0  # ~$2/month (premium tier)
}
```

---

### 4. text-embedding-3-small (RAG)

```python
EMBEDDING_CONFIG = {
    "model": "text-embedding-3-small",
    "dimensions": 1536,  # Default dimensions
    "timeout": 5.0
}

# Pricing
EMBEDDING_PRICING = {
    "cost_per_1m_tokens": 0.02,  # $0.02 / 1M
    "expected_usage": 500 * 10,  # 500 tasks × 10 tokens avg
    "monthly_cost": 0.005 * 0.02  # ~$0.0001/month (negligible!)
}
```

---

## 💰 Complete Cost Breakdown

### Monthly AI Costs (500 tasks/month)

| Operation | Model | Usage | Cost |
|-----------|-------|-------|------|
| **Voice transcription** | Whisper | 250 min | $1.50 |
| **Task parsing** | GPT-5 Nano | 350K tokens | $0.02 |
| **Time estimation** | GPT-5 Nano | 1M tokens | $0.05 |
| **Embeddings** | text-emb-3-small | 5K tokens | $0.0001 |
| **Weekly analytics** | GPT-5 | 200K tokens | $2.00 |
| **Buffer** | - | - | $0.50 |
| **TOTAL** | - | - | **$4.07/month** |

**Combined with infrastructure** ($6 Droplet): **$10/month total** ✅

---

## 🚀 Fallback Strategy

### Model Availability

```python
MODEL_FALLBACKS = {
    "gpt-5-nano": [
        "gpt-5-nano",      # Primary
        "gpt-4o-mini",     # Fallback 1 (3x cost but reliable)
        "gpt-4o"           # Fallback 2 (premium but always available)
    ],
    
    "gpt-5": [
        "gpt-5",           # Primary
        "gpt-4o",          # Fallback 1
        "claude-3.5-sonnet"  # Fallback 2 (different provider)
    ],
    
    "whisper-1": [
        "whisper-1"        # No fallback (highly reliable)
    ]
}


async def call_with_fallback(
    operation: str,
    prompt: str,
    config: dict
) -> str:
    """Call AI with automatic fallback."""
    
    models = MODEL_FALLBACKS[config["model"]]
    
    for model in models:
        try:
            return await ai_client.call(
                model=model,
                prompt=prompt,
                **config
            )
        except (RateLimitError, ModelUnavailable) as e:
            logger.warning(f"Model {model} unavailable: {e}")
            continue  # Try next model
    
    raise AllModelsFailed("All fallback models failed")
```

---

## 📊 Rate Limiting

### OpenAI Rate Limits

```python
RATE_LIMITS = {
    "gpt-5-nano": {
        "requests_per_minute": 3000,  # Very high
        "tokens_per_minute": 1_000_000
    },
    
    "gpt-5": {
        "requests_per_minute": 500,
        "tokens_per_minute": 150_000
    },
    
    "whisper-1": {
        "requests_per_minute": 50
    }
}
```

**Our Usage**: Far below limits (20-30 requests/day)

---

## 🔍 Monitoring

### Track AI Usage

```python
# Log every AI call
logger.info(
    "ai_api_call",
    model=model_name,
    operation=operation,
    input_tokens=input_tokens,
    output_tokens=output_tokens,
    duration_ms=duration_ms,
    cost_usd=calculated_cost,
    success=True
)

# Aggregate monthly
async def get_monthly_ai_costs() -> dict:
    """Calculate AI costs for current month."""
    
    logs = await get_ai_logs(current_month)
    
    return {
        "whisper": sum_costs(logs, "whisper-1"),
        "gpt_5_nano": sum_costs(logs, "gpt-5-nano"),
        "gpt_5": sum_costs(logs, "gpt-5"),
        "embeddings": sum_costs(logs, "text-embedding-3-small"),
        "total": sum_all_costs(logs)
    }
```

---

## ⚡ Performance Targets

| Operation | Model | Target | Typical |
|-----------|-------|--------|---------|
| **Voice transcription** | Whisper | < 3s | ~2s |
| **Task parsing** | GPT-5 Nano | < 2s | ~1s |
| **Time estimation** | GPT-5 Nano | < 2s | ~1s |
| **Weekly analytics** | GPT-5 | < 30s | ~12s |
| **Embedding** | text-emb-3-small | < 1s | ~0.2s |

---

## 🎯 Quality Metrics

### Accuracy Targets

| Operation | Initial | Target (1 month) | Metric |
|-----------|---------|------------------|--------|
| **Business detection** | 85% | 90% | Correct business_id |
| **Deadline parsing** | 80% | 85% | Correct datetime |
| **Time estimation** | 50% | 80% | Within 20% of actual |
| **Transcription** | 95% | 95% | WER (Word Error Rate) |

### Tracking

```python
async def track_accuracy(
    operation: str,
    predicted: any,
    actual: any
) -> float:
    """Track prediction accuracy."""
    
    accuracy = calculate_accuracy(predicted, actual)
    
    await metrics.record(
        metric_name=f"{operation}_accuracy",
        value=accuracy,
        tags={"operation": operation}
    )
    
    return accuracy
```

---

## 📖 Prompt Library Location

```
docs/05-ai-specifications/prompts/
├── task-parser.md           ✅ Created
├── time-estimator.md         ✅ Created
├── weekly-analytics.md       ✅ Created
├── business-detector.md      (similar to parser)
├── deadline-parser.md        (similar to parser)
├── priority-calculator.md    (simple rules)
└── daily-optimizer.md        (task sorting)
```

**Status**: Core prompts documented (3 most critical)

---

## 📝 References

- ADR-001: LangGraph
- ADR-002: GPT-5 Nano Choice
- ADR-004: RAG Strategy
- Prompts: `docs/05-ai-specifications/prompts/`

---

**Status**: ✅ AI Models Configuration Complete  
**Total AI Cost**: $4/month (within $3-5 budget)  
**Models**: 4 (Whisper, GPT-5 Nano, GPT-5, Embeddings)  
**Tier 1+2**: GPT-5 Nano (ultra cheap)  
**Tier 3**: GPT-5 (weekly analytics only)

