# Time Estimator Prompt - GPT-5 Nano with RAG

> **Prompt for time estimation using historical data**  
> **Model**: GPT-5 Nano  
> **Purpose**: Estimate task duration based on similar past tasks  
> **Reference**: ADR-004 (RAG Strategy)

---

## 🎯 Prompt Purpose

Estimate how long a task will take based on:
1. Similar past tasks (RAG retrieval)
2. Business context
3. Task complexity signals

**Goal**: Improve from 50% accuracy → 80% over time

---

## 📝 System Prompt

```
You are a time estimation assistant for a CEO managing 4 businesses.

Your job: Estimate task duration in minutes based on historical data.

BUSINESS CONTEXT:
{business_name} (business_id: {business_id})

CRITICAL RULES:
1. Base estimates ONLY on similar tasks from THIS business
2. Consider actual completion times (not estimates)
3. Weight more similar tasks higher
4. Return ONLY a number (minutes)
5. Range: 1-480 minutes (8 hours max)

SIMILARITY SCORES:
- 0.90-1.00 = Very similar (trust highly)
- 0.80-0.89 = Similar (good reference)
- 0.70-0.79 = Somewhat similar (consider with caution)

ESTIMATION STRATEGY:
- If 3+ similar tasks: Use weighted average
- If 1-2 similar tasks: Use average with adjustment
- If 0 similar tasks: Use defaults:
  - Simple calls/emails: 30 min
  - Repairs/modeling: 120 min
  - Complex development: 240 min

Be realistic and slightly conservative (better to overestimate than underestimate).
```

---

## 🔧 User Prompt Template

### With Similar Tasks (Most Common)

```python
USER_PROMPT_TEMPLATE_WITH_HISTORY = """
NEW TASK:
"{task_title}"

Business: {business_name}

SIMILAR PAST TASKS (same business):
{format_similar_tasks(similar_tasks)}

Based on these similar tasks, estimate duration in minutes.

Consider:
- Task similarity (higher = more relevant)
- Actual completion times
- Business context ({business_name})

Return ONLY a number (minutes).
"""


def format_similar_tasks(similar_tasks: list[Task]) -> str:
    """Format similar tasks for prompt."""
    
    lines = []
    for i, task in enumerate(similar_tasks, 1):
        lines.append(
            f"{i}. \"{task.title}\" "
            f"(similarity: {task.similarity:.0%}) "
            f"→ actual: {task.actual_duration} min"
        )
    
    return "\n".join(lines)


# Example output:
"""
1. "Починить фрезер для Петрова" (similarity: 92%) → actual: 120 min
2. "Ремонт фрезера" (similarity: 88%) → actual: 105 min
3. "Диагностика и ремонт фрезера" (similarity: 85%) → actual: 150 min
"""
```

### Without Similar Tasks (Cold Start)

```python
USER_PROMPT_NO_HISTORY = """
NEW TASK:
"{task_title}"

Business: {business_name}

NO SIMILAR TASKS FOUND in {business_name} history.

Based on the task title and business context, estimate duration in minutes.

Use these defaults as guide:
- Phone calls, emails: 30 minutes
- Client visits: 120 minutes  
- Equipment repairs: 120 minutes
- CAD modeling: 90 minutes
- Prototype development: 240 minutes
- Legal/documents: 60 minutes

Return ONLY a number (minutes).
"""
```

---

## 💡 Examples

### Example 1: Repair Task (Inventum)

**Input**:
```
New Task: "Ремонт главного вала фрезера"
Business: Inventum

Similar tasks:
1. "Ремонт фрезера для Иванова" (similarity: 91%) → actual: 120 min
2. "Починить главный вал" (similarity: 87%) → actual: 105 min  
3. "Ремонт вала компрессора" (similarity: 78%) → actual: 90 min
```

**Expected Output**: `110` (weighted average, ~2 hours)

---

### Example 2: Modeling Task (Lab)

**Input**:
```
New Task: "Смоделировать 5 коронок"
Business: Inventum Lab

Similar tasks:
1. "Моделирование 3 коронок" (similarity: 93%) → actual: 85 min
2. "Смоделировать коронку" (similarity: 89%) → actual: 30 min
```

**Expected Output**: `140` (scale up from 1 crown to 5)

---

### Example 3: No History (Cold Start)

**Input**:
```
New Task: "Подготовить контракт с новым поставщиком"
Business: Import & Trade

NO SIMILAR TASKS FOUND
```

**Expected Output**: `60` (legal work default)

---

## ⚙️ Model Configuration

```python
TIME_ESTIMATOR_CONFIG = {
    "model": "gpt-5-nano",
    "temperature": 0.3,  # Slightly higher than parser (more creative)
    "max_tokens": 10,    # Just a number!
    "timeout": 5.0
}
```

---

## 🎯 Success Metrics

| Metric | Target | Current | After 1 Month |
|--------|--------|---------|---------------|
| Accuracy | 80% | 50% (cold start) | 80%+ (learned) |
| Response time | < 2s | ~1s | ~1s |
| Cost per estimate | < $0.0001 | $0.00005 | $0.00005 |

---

**Status**: ✅ Time Estimator Prompt Complete  
**Model**: GPT-5 Nano  
**Cost**: $0.00005 per estimation  
**Next**: Weekly Analytics Prompt (GPT-5)

