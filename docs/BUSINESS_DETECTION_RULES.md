# Business Detection Rules

> **Last Updated**: 2025-10-20
> **Related**: GPT-5 Nano task parser system prompt

## Overview

This document describes the priority-based rules for detecting which business (Inventum, Inventum Lab, R&D, or Import & Trade) a task belongs to when parsing voice messages.

## Priority Hierarchy

The parser uses a **3-level priority system** to determine the correct business:

### Priority 1: Location Keywords (HIGHEST)

If a location is explicitly mentioned, it **always** overrides all other rules.

| Location Keyword | Business | ID | Example |
|-----------------|----------|----|---------|
| "мастерская" | Inventum | 1 | "Максим работает над разработкой **для мастерской**" |
| "лаборатория" | Inventum Lab | 2 | "Дима доставит материалы **в лабораторию**" |

**Rationale**: Location explicitly defines the physical workspace where the task will be performed. Location has **highest priority** and overrides all other rules (even "разработка" keyword).

### Priority 2: Team Member + "разработка" Keyword

If **Максим** or **Дима** is mentioned (they work primarily in Inventum repair), the business is determined by whether **"разработка"** is explicitly mentioned:

#### Rule 2A: WITH "разработка" → R&D (id:3) [RARE CASE]

If the message **explicitly** contains the word **"разработка"**:

**Examples**:
```
"Максим ведет разработку нового устройства" → R&D (id:3)
"Дима работает над разработкой прототипа" → R&D (id:3)
"Максим занимается разработкой системы управления" → R&D (id:3)
```

#### Rule 2B: WITHOUT "разработка" → Inventum (id:1) [DEFAULT]

If "разработка" is NOT mentioned, the task defaults to **Inventum repair workshop**.

**Examples**:
```
"Максим должен починить фрезер" → Inventum (id:1)
"Дима проведет диагностику оборудования" → Inventum (id:1)
"Максим выедет к клиенту завтра" → Inventum (id:1)
"Дима соберет плату управления" → Inventum (id:1) [no "разработка" → Inventum]
"Максим должен сделать прототип" → Inventum (id:1) [no "разработка" → Inventum]
```

**Rationale**:
- Максим and Дима **primarily** work in the repair workshop (Inventum) - this is 95% of tasks
- They **rarely** work on R&D projects (development direction)
- User will **explicitly mention** "разработка" when it's an R&D task
- Default to their main role (Inventum) unless "разработка" is clearly stated

### Priority 3: General Keywords (LOWEST)

If no location or team member is mentioned, use general keywords to detect business:

| Business | Keywords |
|----------|----------|
| **Inventum (id:1)** | фрезер, ремонт, диагностика, сервис, клиент |
| **Inventum Lab (id:2)** | коронка, моделирование, CAD, CAM, фрезеровка, протез |
| **R&D (id:3)** | прототип, плата, разработка, сборка, тест, электроника |
| **Import & Trade (id:4)** | поставщик, Китай, контракт, таможня, импорт, логистика |

**Examples**:
```
"Починить фрезер для клиента" → Inventum (id:1) [keyword: фрезер, клиент]
"Смоделировать коронку" → Inventum Lab (id:2) [keyword: коронка]
"Разработать новую плату" → R&D (id:3) [keyword: плату]
"Связаться с поставщиком в Китае" → Import & Trade (id:4) [keyword: Китай]
```

## Team Roster

Understanding team composition helps explain the rules:

| Business | Team Members | Notes |
|----------|-------------|-------|
| **Inventum (id:1)** | Максим (Директор), Дима (Мастер), Максут (Выездной) | Main repair workshop |
| **Inventum Lab (id:2)** | Юрий Владимирович (Директор), Мария (CAD/CAM оператор) | Dental lab |
| **R&D (id:3)** | Максим, Дима | Same people from Inventum, part-time |
| **Import & Trade (id:4)** | Слава (Юрист/бухгалтер) | - |

**Key Insight**: Максим and Дима work in **both** Inventum and R&D, hence the need for Priority 2 rules.

## Complex Examples

### Example 1: Location Override (мастерская)

**Input**: "Максим работает над разработкой для мастерской"

**Analysis**:
- Team member: Максим ✓
- Keyword: "разработкой" ✓ (would trigger R&D)
- **Location: "для мастерской"** ← Priority 1 override!

**Result**: Inventum (id:1) - Location rule overrides "разработка" keyword

---

### Example 2: Team Member with "разработка"

**Input**: "Дима ведет разработку нового прототипа"

**Analysis**:
- Team member: Дима ✓
- **Keyword: "разработку"** ✓ ← Explicitly mentioned!
- No location mentioned ✗

**Result**: R&D (id:3) - "разработка" explicitly mentioned

---

### Example 3: Team Member Default to Inventum

**Input**: "Максим должен сделать прототип корпуса"

**Analysis**:
- Team member: Максим ✓
- No "разработка" keyword ✗ (only "прототип")
- No location mentioned ✗

**Result**: Inventum (id:1) - Default for Максим/Дима without "разработка"

---

### Example 4: Pure Keyword Detection

**Input**: "Позвонить поставщику в Китае по контракту"

**Analysis**:
- No team member mentioned ✗
- No location mentioned ✗
- Keywords: "поставщику", "Китае", "контракту" → Import & Trade

**Result**: Import & Trade (id:4) - General keyword matching

## Implementation

### System Prompt

The rules are encoded in the GPT-5 Nano system prompt:

**File**: [src/infrastructure/external/openai_client.py](../src/infrastructure/external/openai_client.py#L297-L306)

```python
CRITICAL RULES - Business Detection Priority:
1. Location mentioned:
   - "мастерская" → ALWAYS id:1 (Inventum repair)
   - "лаборатория" → ALWAYS id:2 (Inventum Lab)

2. Максим or Дима mentioned (they work mainly in Inventum repair):
   - If "разработка" explicitly mentioned → id:3 (R&D) [RARE CASE]
   - Otherwise → id:1 (Inventum repair) [DEFAULT - most tasks]

3. If no location/team, use keywords to detect business.
```

### Unit Tests

The rules are validated by 3 comprehensive tests:

**File**: [tests/unit/test_task_parser.py](../tests/unit/test_task_parser.py#L486-L580)

1. **test_business_detection_maxim_dima_repair_by_default**
   - Tests Priority 2B: Максим/Дима WITHOUT "разработка" → Inventum (default)
   - 4 test cases covering repair, diagnostics, client visits

2. **test_business_detection_maxim_dima_with_rnd_keywords**
   - Tests Priority 2A: Максим/Дима WITH explicit "разработка" → R&D
   - 4 test cases all containing "разработка" keyword

3. **test_business_detection_location_overrides_team_rule**
   - Tests Priority 1: Location overrides all other rules (even "разработка")
   - 3 test cases: мастерская override, лаборатория, and "разработка" without location

## Testing Checklist

Use this checklist to verify the rules work correctly:

**Priority 2B: Default to Inventum (without "разработка")**
- [ ] "Максим должен починить фрезер" → Inventum (id:1)
- [ ] "Дима проведет диагностику" → Inventum (id:1)
- [ ] "Максим должен сделать прототип" → Inventum (id:1) [no "разработка"]
- [ ] "Дима соберет плату управления" → Inventum (id:1) [no "разработка"]

**Priority 2A: Explicit "разработка" → R&D**
- [ ] "Максим ведет разработку нового устройства" → R&D (id:3)
- [ ] "Дима работает над разработкой прототипа" → R&D (id:3)

**Priority 1: Location Override**
- [ ] "Максим работает над разработкой для мастерской" → Inventum (id:1) [location overrides "разработка"]
- [ ] "Дима доставит материалы в лабораторию" → Inventum Lab (id:2)

**Priority 3: General Keywords (no team)**
- [ ] "Починить фрезер" → Inventum (id:1)
- [ ] "Смоделировать коронку" → Inventum Lab (id:2)

## Change History

| Date | Change | Reason |
|------|--------|--------|
| 2025-10-20 (v2) | **SIMPLIFIED**: Only "разработка" keyword triggers R&D. Removed "workshop", "прототип", "плата", "электроника" keywords. | User feedback: "Важно то что я буду явно упоминать что данная задача касается направления разработки. Основная деятельность Максима и Димы касается в основном мастерской Inventum. Workshop английское я никогда не буду использовать." |
| 2025-10-20 (v1) | Added Priority 2: Максим/Дима default to Inventum unless multiple R&D keywords present | User feedback: "когда я говорю Максим или Дима и при этом не упомянул явно что задача касается направления разработки то значит эта задача относиться к мастерской Inventum" |
| 2025-10-18 | Added Priority 1: Location keywords ("мастерская", "лаборатория") | User feedback: "мастерская" was incorrectly mapped to R&D |
| 2025-10-15 | Initial keyword-based detection | Original implementation |

## Related Documentation

- [Task Parser Prompt](../05-ai-specifications/prompts/task-parser.md)
- [LangGraph Workflow](../05-ai-specifications/langgraph-flows.md)
- [GPT-5 Nano Prompt Optimization](PROMPT_OPTIMIZATION.md)
