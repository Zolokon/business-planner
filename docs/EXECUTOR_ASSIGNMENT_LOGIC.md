# Executor Assignment Logic

> **Business Rule**: How tasks are assigned to executors based on voice/text input

## 📋 Overview

When creating tasks via voice or text, the system intelligently determines who should execute the task based on the input.

## 🎯 The Rule

### **If team member is explicitly mentioned → assign to them**
```
"Максим должен починить фрезер"
→ assigned_to: "Максим"

"Дима сделает прототип"
→ assigned_to: "Дима"

"Мария смоделирует коронки"
→ assigned_to: "Мария"
```

### **If "я" (I) or "мне" (to me) mentioned → assign to CEO (null)**
```
"Мне нужно позвонить клиенту"
→ assigned_to: null (task for CEO)

"Я должен проверить контракт"
→ assigned_to: null (task for CEO)
```

### **If NO executor mentioned → assign to CEO (null)**
```
"Нужно починить фрезер"
→ assigned_to: null (task for CEO)

"Позвонить поставщику"
→ assigned_to: null (task for CEO)

"Проверить документы"
→ assigned_to: null (task for CEO)
```

## 💡 Why This Matters

As a CEO managing multiple businesses, you need to:
1. **Delegate** tasks to team members when appropriate
2. **Keep** tasks for yourself when no one else is mentioned
3. **Explicitly state** when something is for you ("мне", "я")

## 🔧 Implementation

This logic is implemented in:
- **GPT-5 Nano Prompt**: `src/infrastructure/external/openai_client.py` (lines 298-307)
- **Documentation**: `docs/05-ai-specifications/prompts/task-parser.md` (Rule #6)

## 📊 Examples

| Input | assigned_to | Reason |
|-------|-------------|--------|
| "Максим должен починить фрезер" | "Максим" | Explicitly mentioned |
| "Починить фрезер" | `null` | No executor = CEO |
| "Мне позвонить клиенту" | `null` | "Мне" = CEO |
| "Я проверю контракт" | `null` | "Я" = CEO |
| "Дима сделает прототип" | "Дима" | Explicitly mentioned |
| "Слава подготовит документы" | "Слава" | Explicitly mentioned |
| "Нужно заказать материалы" | `null` | No executor = CEO |

## 🧪 Tests

This logic is covered by **4 unit tests**:
- `test_executor_assignment_team_member_mentioned` ✅
- `test_executor_assignment_no_mention_is_for_ceo` ✅
- `test_executor_assignment_self_reference` ✅
- `test_executor_assignment_different_team_members` ✅

Location: `tests/unit/test_task_parser.py` (lines 383-479)

## 🚀 Usage in Telegram Bot

When you send a voice message or text to the bot:

```
🎤 Voice: "Максим должен починить фрезер до завтра"

Bot creates task:
✅ Title: Починить фрезер
👤 Assigned to: Максим
📅 Deadline: завтра
```

```
🎤 Voice: "Нужно позвонить поставщику в Китае"

Bot creates task:
✅ Title: Позвонить поставщику в Китае
👤 Assigned to: [you] (null in database)
📅 Deadline: —
```

## 🔄 Database Model

In the database:
- `assigned_to` field stores **member_id** (integer) or **NULL**
- NULL means task is assigned to the CEO (you)
- When displaying, NULL is shown as "[you]" or your name

## 📝 Notes

1. **Team members** are recognized by name:
   - Максим, Дима, Максут, Юрий Владимирович, Мария, Слава, Константин, Лиза

2. **Case insensitive**: "максим" and "Максим" both work

3. **Flexible phrasing**:
   - "Максим должен..."
   - "Дима сделает..."
   - "Мария, смоделируй..."
   - "Слава подготовит..."

4. **Self-references**:
   - "я", "мне", "мной", "меня" → assigned_to = null

## 🎓 Best Practices

**For delegation:**
```
✅ "Максим должен починить фрезер"
✅ "Дима сделает прототип"
✅ "Слава подготовит документы"
```

**For self-assignment:**
```
✅ "Мне позвонить клиенту"
✅ "Я проверю контракт"
✅ "Позвонить поставщику" (implicit)
```

**What to avoid:**
```
❌ "Кто-то должен починить" (ambiguous)
❌ "Надо бы кому-то позвонить" (unclear)
```

Be specific = better task assignment! 🎯
