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
| "мастерская" | Inventum | 1 | "Максим должен сделать прототип **для мастерской**" |
| "лаборатория" | Inventum Lab | 2 | "Дима доставит материалы **в лабораторию**" |
| "workshop" | R&D | 3 | "Максим должен починить фрезер **в workshop**" |

**Rationale**: Location explicitly defines the physical workspace where the task will be performed.

### Priority 2: Team Member + Context

If **Максим** or **Дима** is mentioned (they work in both Inventum and R&D), the business is determined by context:

#### Rule 2A: With R&D Keywords → R&D (id:3)

If the message contains R&D-related keywords:
- прототип (prototype)
- плата (board/PCB)
- разработка (development)
- сборка (assembly)
- электроника (electronics)
- тест (test)
- workshop (English)

**Examples**:
```
"Максим должен сделать прототип корпуса" → R&D (id:3)
"Дима соберет плату управления" → R&D (id:3)
"Максим протестирует новую разработку" → R&D (id:3)
```

#### Rule 2B: Without R&D Keywords → Inventum (id:1)

If no R&D keywords are present, the task defaults to **Inventum repair workshop**.

**Examples**:
```
"Максим должен починить фрезер" → Inventum (id:1)
"Дима проведет диагностику оборудования" → Inventum (id:1)
"Максим выедет к клиенту завтра" → Inventum (id:1)
```

**Rationale**:
- Максим and Дима primarily work in the repair workshop (Inventum)
- They occasionally help with R&D projects
- Default to their main role unless R&D context is clear

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

### Example 1: Location Override

**Input**: "Максим должен сделать прототип для мастерской"

**Analysis**:
- Team member: Максим ✓
- R&D keyword: "прототип" ✓
- **Location: "для мастерской"** ← Priority 1 override!

**Result**: Inventum (id:1) - Location rule overrides R&D keywords

---

### Example 2: Team Member with R&D Context

**Input**: "Дима соберет плату управления в workshop"

**Analysis**:
- Team member: Дима ✓
- R&D keywords: "плату" (board/PCB) ✓
- Location: "workshop" ✓ (but matches R&D anyway)

**Result**: R&D (id:3) - Team member + R&D keywords

---

### Example 3: Team Member Default to Inventum

**Input**: "Максим выедет к клиенту завтра"

**Analysis**:
- Team member: Максим ✓
- No R&D keywords ✗
- No location mentioned ✗

**Result**: Inventum (id:1) - Default for Максим/Дима without R&D context

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

**File**: [src/infrastructure/external/openai_client.py](../src/infrastructure/external/openai_client.py#L298-L308)

```python
CRITICAL RULES - Business Detection Priority:
1. Location mentioned:
   - "мастерская" → ALWAYS id:1 (Inventum repair)
   - "лаборатория" → ALWAYS id:2 (Inventum Lab)
   - "workshop" → ALWAYS id:3 (R&D)

2. Team member mentioned (Максим/Дима):
   - If R&D keywords (прототип, плата, разработка, workshop) → id:3 (R&D)
   - Otherwise → id:1 (Inventum repair)

3. If no location/team, use keywords to detect business.
```

### Unit Tests

The rules are validated by 3 comprehensive tests:

**File**: [tests/unit/test_task_parser.py](../tests/unit/test_task_parser.py#L486-L580)

1. **test_business_detection_maxim_dima_repair_by_default**
   - Tests Priority 2B: Максим/Дима without R&D keywords → Inventum
   - 4 test cases covering repair, diagnostics, client visits

2. **test_business_detection_maxim_dima_with_rnd_keywords**
   - Tests Priority 2A: Максим/Дима with R&D keywords → R&D
   - 4 test cases covering prototypes, electronics, development

3. **test_business_detection_location_overrides_team_rule**
   - Tests Priority 1: Location overrides all other rules
   - 3 test cases covering all location keywords

## Testing Checklist

Use this checklist to verify the rules work correctly:

- [ ] "Максим должен починить фрезер" → Inventum (id:1)
- [ ] "Дима проведет диагностику" → Inventum (id:1)
- [ ] "Максим должен сделать прототип" → R&D (id:3)
- [ ] "Дима соберет плату управления" → R&D (id:3)
- [ ] "Максим должен сделать прототип для мастерской" → Inventum (id:1) [location override]
- [ ] "Максим должен починить фрезер в workshop" → R&D (id:3) [location override]
- [ ] "Починить фрезер" (no team) → Inventum (id:1) [keyword]
- [ ] "Смоделировать коронку" (no team) → Inventum Lab (id:2) [keyword]

## Change History

| Date | Change | Reason |
|------|--------|--------|
| 2025-10-20 | Added Priority 2: Максим/Дима default to Inventum unless R&D keywords present | User feedback: "когда я говорю Максим или Дима и при этом не упомянул явно что задача касается направления разработки то значит эта задача относиться к мастерской Inventum" |
| 2025-10-18 | Added Priority 1: Location keywords | User feedback: "мастерская" was incorrectly mapped to R&D |
| 2025-10-15 | Initial keyword-based detection | Original implementation |

## Related Documentation

- [Task Parser Prompt](../05-ai-specifications/prompts/task-parser.md)
- [LangGraph Workflow](../05-ai-specifications/langgraph-flows.md)
- [GPT-5 Nano Prompt Optimization](PROMPT_OPTIMIZATION.md)
