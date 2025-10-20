# Task Parser Prompt - GPT-5 Nano

> **Prompt for parsing voice/text into structured task**  
> **Model**: GPT-5 Nano  
> **Purpose**: Extract task structure from Russian transcript  
> **Reference**: ADR-002 (GPT-5 Nano), Bounded Contexts

---

## 🎯 Prompt Purpose

Parse unstructured Russian text (voice transcript or text message) into structured task data.

**Extract**:
- Task title (what to do)
- Business context (1-4)
- Deadline (natural language)
- Project name (if mentioned)
- Assigned to (team member name)
- Priority signals

---

## 📝 System Prompt (Optimized)

**Version**: 2.0 (Optimized - 57% token reduction)
**Tokens**: ~245 (down from ~564)

```
Parse Russian task from voice/text for CEO managing 4 businesses in Almaty.

BUSINESSES:
1. INVENTUM (id:1) - Dental equipment repair | Team: Максим, Дима, Максут
2. INVENTUM LAB (id:2) - Dental lab CAD/CAM | Team: Юрий Владимирович, Мария
3. R&D (id:3) - Prototyping & development | Team: Максим, Дима
4. IMPORT & TRADE (id:4) - Equipment import from China | Team: Слава

RULES:
1. business_id (1-4) - REQUIRED
2. assigned_to: team member name if mentioned, null if "я"/"мне"/not mentioned (CEO task)
   Examples: "Дима починит" → "Дима" | "Починить" → null | "Мне позвонить" → null

JSON OUTPUT:
{"title": "string", "business_id": 1-4, "deadline": "string|null", "project": "string|null", "assigned_to": "name|null", "priority": 1-4}
```

### Optimization Notes

**What was removed** (without losing effectiveness):
- Verbose keyword lists (GPT-5 Nano infers from business descriptions)
- Redundant team position descriptions
- Expanded JSON format (GPT understands compact notation)
- Cross-business team section (Константин, Лиза not frequently mentioned)
- Duplicate rule explanations

**What was kept** (critical for accuracy):
- 4 business contexts with team names
- business_id requirement
- Executor assignment logic with 3 examples
- JSON output structure

EXAMPLES:

Input: "Завтра утром Дима должен починить фрезер для Иванова"
Output: {
  "title": "Починить фрезер для Иванова",
  "business_id": 1,
  "deadline": "завтра утром",
  "project": null,
  "assigned_to": "Дима",
  "priority": 1,
  "description": null
}

Input: "Мария, смоделируй 3 коронки к пятнице, проект Заказ на 10 коронок"
Output: {
  "title": "Смоделировать 3 коронки",
  "business_id": 2,
  "deadline": "пятница",
  "project": "Заказ на 10 коронок",
  "assigned_to": "Мария",
  "priority": 2,
  "description": null
}

Input: "Позвонить новому поставщику из Китая, это срочно"
Output: {
  "title": "Позвонить новому поставщику из Китая",
  "business_id": 4,
  "deadline": null,
  "project": null,
  "assigned_to": null,  // No executor mentioned = for CEO
  "priority": 1,
  "description": "Срочно"
}

Input: "Мне нужно проверить контракт с Китаем"
Output: {
  "title": "Проверить контракт с Китаем",
  "business_id": 4,
  "deadline": null,
  "project": null,
  "assigned_to": null,  // "Мне" = for CEO
  "priority": 2,
  "description": null
}

Input: "Слава должен подготовить документы для таможни"
Output: {
  "title": "Подготовить документы для таможни",
  "business_id": 4,
  "deadline": null,
  "project": null,
  "assigned_to": "Слава",  // Explicitly delegated to Слава
  "priority": 2,
  "description": null
}

Input: "Разработать прототип нового наконечника, нужно к следующей неделе"
Output: {
  "title": "Разработать прототип нового наконечника",
  "business_id": 3,
  "deadline": "следующая неделя",
  "project": null,
  "assigned_to": null,
  "priority": 2,
  "description": null
}
```

---

## 🔧 User Prompt Template

```python
USER_PROMPT_TEMPLATE = """
CONTEXT (recent activity):
{recent_tasks_summary}

CURRENT INPUT:
"{transcript}"

Parse this into structured task JSON.
Remember: business_id is MANDATORY (1-4).
"""
```

---

## 🎯 Few-Shot Examples (In Prompt)

Include 3-5 examples in system prompt to improve accuracy.

**Why**: GPT-5 Nano learns from examples (few-shot learning)

---

## ⚙️ Model Parameters

```python
TASK_PARSER_CONFIG = {
    "model": "gpt-5-nano",
    "temperature": 0.1,  # Low for consistency
    "max_tokens": 500,
    "response_format": {"type": "json_object"},
    "timeout": 5.0  # seconds
}
```

---

## 📊 Expected Performance

- **Accuracy**: > 90% (business detection)
- **Speed**: < 1 second
- **Cost**: $0.00003 per task
- **Language**: Russian

---

**Next**: Time Estimator Prompt

