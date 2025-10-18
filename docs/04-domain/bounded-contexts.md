# Bounded Contexts - Business Planner

> **Domain-Driven Design: Context Boundaries**  
> **Created**: 2025-10-17  
> **Reference**: ADR-003 (Business Isolation)

---

## 🎯 What are Bounded Contexts?

**Bounded Context** = A clear boundary within which a domain model is valid

In Business Planner, each of the **4 businesses** is a separate bounded context with its own meaning for common terms.

---

## 🏢 The 4 Bounded Contexts

### Overview

```
Business Planner System
│
├── 🔧 Inventum Context (Dental Equipment Repair)
├── 🦷 Inventum Lab Context (Dental Laboratory)
├── 🔬 R&D Context (Research & Development)
└── 💼 Import & Trade Context (Equipment Import)
```

**Critical Principle** (ADR-003):
> "The same word can mean different things in different contexts"

---

## 1️⃣ Inventum Context (Dental Equipment Repair)

### Domain
Repair and maintenance of dental equipment for clients

### Ubiquitous Language

| Term | Meaning in Inventum | Example |
|------|---------------------|---------|
| **Диагностика** | Equipment diagnostics | "Диагностика платы фрезера" |
| **Ремонт** | Client equipment repair | "Ремонт наконечника для Иванова" |
| **Выезд** | On-site client visit | "Выезд к клиенту Петрову" |
| **Фрезер** | Milling machine (equipment) | "Починить фрезер" |
| **Клиент** | Customer needing repair | "Иванов", "Петров" |
| **Плата** | Circuit board | "Замена платы" |

### Key Entities
- **RepairTask** - Task to fix client equipment
- **Client** - Customer who owns equipment
- **Equipment** - Device being repaired
- **ServiceVisit** - On-site visit

### Business Rules
- Repairs have client names (e.g., "для Иванова")
- Выездной tasks assigned to Максут
- Workshop repairs assigned to Дима
- Management tasks to Максим
- Typical duration: 1-4 hours

### Team Members (Inventum-specific)
- Максим (Директор)
- Дима (Мастер)
- Максут (Выездной мастер)

---

## 2️⃣ Inventum Lab Context (Dental Laboratory)

### Domain
Production of dental prosthetics and appliances

### Ubiquitous Language

| Term | Meaning in Lab | Example |
|------|----------------|---------|
| **Моделирование** | CAD modeling | "Моделирование коронки" |
| **Фрезеровка** | CNC milling | "Фрезеровка протеза" |
| **Коронка** | Dental crown | "Сделать 5 коронок" |
| **CAD/CAM** | Design & manufacturing | "CAD работа" |
| **Заказ** | Production order | "Заказ на 10 коронок" |
| **Клиент** | Dental clinic customer | Different from Inventum clients |

### Key Entities
- **ProductionTask** - Task to produce dental items
- **ProductionOrder** - Batch of items to produce
- **DentalItem** - Crown, bridge, prosthetic
- **DigitalModel** - CAD model

### Business Rules
- CAD/CAM tasks assigned to Мария
- Quality control by Юрий Владимирович
- Production in batches (коронки, мосты)
- Typical duration: 1-3 hours per item

### Team Members (Lab-specific)
- Юрий Владимирович (Директор)
- Мария (CAD/CAM оператор)

---

## 3️⃣ R&D Context (Research & Development)

### Domain
Prototype development and innovation

### Ubiquitous Language

| Term | Meaning in R&D | Example |
|------|----------------|---------|
| **Прототип** | Prototype being developed | "Прототип нового наконечника" |
| **Тест** | Prototype testing | "Тест прототипа" (NOT equipment test) |
| **Разработка** | Design and development | "Разработать новую версию" |
| **Workshop** | R&D location | "В workshop" |
| **Документация** | Technical documentation | "Задокументировать прототип" |
| **Эксперимент** | Testing new approaches | "Эксперимент с материалами" |

### Key Entities
- **PrototypeTask** - Development task
- **Prototype** - Thing being developed
- **TestResult** - Results from testing
- **TechnicalDoc** - Documentation

### Business Rules
- Location always "Workshop"
- Assigned to Максим, Дима (cross-functional from Inventum)
- Longer duration (2-8 hours typical)
- Experimental nature (estimates less accurate initially)

### Team Members (R&D-specific)
- Максим (from Inventum)
- Дима (from Inventum)

**Note**: Same people, but different context than Inventum!

---

## 4️⃣ Import & Trade Context (Equipment Import)

### Domain
Import of equipment from China, logistics, legal

### Ubiquitous Language

| Term | Meaning in Trade | Example |
|------|------------------|---------|
| **Поставщик** | Chinese supplier | "Позвонить поставщику" |
| **Контракт** | Import contract | "Подготовить контракт" |
| **Таможня** | Customs procedures | "Оформить таможню" |
| **Логистика** | Shipping logistics | "Уточнить логистику" |
| **Счет** | Invoice/payment | "Оплатить счет" |
| **Китай** | Source country | "Заказать из Китая" |

### Key Entities
- **ImportTask** - Import-related task
- **Supplier** - Chinese supplier
- **ImportOrder** - Equipment order
- **CustomsDocument** - Legal documents

### Business Rules
- All tasks assigned to Слава (legal/accounting)
- Strategic tasks include Константин
- Involves international communication
- Typical duration: 30 min - 2 hours

### Team Members (Trade-specific)
- Слава (Юрист/бухгалтер)
- Константин (CEO oversight)

---

## 🔗 Context Relationships

### Shared Concepts (Anti-Corruption Layer)

#### User (Global)
- **Константин** exists in all contexts
- But tasks are isolated by context

#### Team Members (Cross-Context)
- **Максим**: Inventum Director context + R&D Developer context
- **Дима**: Inventum Master context + R&D Developer context
- **Лиза**: Marketing context across all businesses

**Implementation**:
```python
# Same person, different contexts
class Member:
    id: int
    name: str
    contexts: list[BusinessContext]  # Can have multiple
    
# Task always has ONE context
class Task:
    id: int
    business_context: BusinessContext  # Single, mandatory
    assigned_to: Member  # Can work in multiple contexts
```

---

### Context Mapping

```
┌────────────────────────────────────────────────────┐
│         Shared Kernel (Core Domain)                │
│  - User (Константин)                               │
│  - Time (UTC+5 timezone)                           │
│  - Priority (1-4 Eisenhower)                       │
└────────────────────────────────────────────────────┘
         │            │            │            │
         ▼            ▼            ▼            ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
    │Inventum │  │   Lab   │  │   R&D   │  │  Trade  │
    │Context  │  │Context  │  │Context  │  │Context  │
    └─────────┘  └─────────┘  └─────────┘  └─────────┘
```

**Shared Kernel** = Concepts shared across all contexts  
**Individual Contexts** = Business-specific meanings

---

## 🎯 Context Isolation Rules (ADR-003)

### MUST Isolate

1. **RAG Search**
   ```python
   # ✅ CORRECT
   similar_tasks = find_similar(embedding, business_context=INVENTUM)
   
   # ❌ WRONG
   similar_tasks = find_similar(embedding)  # Cross-context contamination!
   ```

2. **Analytics**
   ```python
   # ✅ CORRECT: Per-context analytics
   inventum_stats = analyze_context(INVENTUM)
   lab_stats = analyze_context(LAB)
   
   # ❌ WRONG: Mixed analytics
   all_stats = analyze_all()  # Meaningless aggregation
   ```

3. **Task History**
   ```python
   # ✅ CORRECT: Context-specific history
   past_repairs = get_history(user, context=INVENTUM)
   
   # ❌ WRONG
   past_all = get_history(user)  # Wrong learning data
   ```

### CAN Cross Contexts

1. **User Overview**
   ```python
   # ✅ OK: CEO sees all contexts
   all_tasks = {
       INVENTUM: get_tasks(INVENTUM),
       LAB: get_tasks(LAB),
       R_D: get_tasks(R_D),
       TRADE: get_tasks(TRADE)
   }
   ```

2. **Cross-Context Team Members**
   ```python
   # ✅ OK: Максим's tasks from both contexts
   maxim_tasks = get_member_tasks(maxim_id)
   # Returns: Inventum tasks + R&D tasks (separate contexts)
   ```

---

## 💡 Context-Specific Examples

### Example 1: "Диагностика"

**Inventum Context**:
```
Title: "Диагностика платы фрезера"
Meaning: Equipment diagnostics
Duration: 1-2 hours
Team: Дима, Максим
Location: Workshop
```

**R&D Context**:
```
Title: "Диагностика прототипа"
Meaning: Prototype testing/analysis
Duration: 3-4 hours
Team: Максим, Дима
Location: Workshop
```

**Same word, different meaning!** → Must stay isolated

---

### Example 2: "Фрезер"

**Inventum Context**:
```
"Ремонт фрезера"
Meaning: Repair client's milling machine
Type: Service task
Client: Yes (name mentioned)
```

**Inventum Lab Context**:
```
"Фрезеровка коронки"
Meaning: Mill a dental crown using our machine
Type: Production task
Client: Clinic order
```

**Different semantics!** → Isolation critical

---

## 🔍 Context Detection (AI)

### Keywords per Context

```python
CONTEXT_KEYWORDS = {
    BusinessContext.INVENTUM: [
        "фрезер", "ремонт", "диагностика", "починить", 
        "сервис", "выезд", "клиент", "Иванов", "Петров",
        "плата", "наконечник", "компрессор"
    ],
    
    BusinessContext.LAB: [
        "коронка", "моделирование", "CAD", "CAM", 
        "фрезеровка", "зуб", "протез", "лаборатория",
        "мост", "винир", "заказ", "клиника"
    ],
    
    BusinessContext.R_D: [
        "прототип", "разработка", "workshop", "тест",
        "дизайн", "документация", "исследование",
        "эксперимент", "версия", "улучшение"
    ],
    
    BusinessContext.TRADE: [
        "поставщик", "Китай", "контракт", "таможня",
        "логистика", "импорт", "экспорт", "доставка",
        "счет", "оплата", "поставка"
    ]
}
```

### AI Detection Prompt
```
Voice: "Нужно починить фрезер для Иванова"

Matches:
- "починить" → Inventum (keyword match)
- "фрезер" → Inventum OR Lab (ambiguous!)
- "для Иванова" → Inventum (client name pattern)

Decision: INVENTUM context (strongest match)
```

---

## 📋 Context Boundaries

### What Stays Within Context

✅ **Task semantics** - "диагностика" means different things  
✅ **Duration patterns** - Different work takes different time  
✅ **Team assignments** - Context-specific teams  
✅ **Historical learning** - RAG searches within context  
✅ **Keywords** - Context-specific vocabulary  

### What Crosses Contexts

✅ **User identity** - Константин is same across all  
✅ **Time zones** - UTC+5 applies to all  
✅ **Priority rules** - Eisenhower matrix same for all  
✅ **Cross-functional members** - Максим, Дима, Лиза  
✅ **System-level features** - Authentication, logging  

---

## 🎯 Implementation in Code

### Domain Layer Structure

```
src/domain/
├── shared/                      # Shared Kernel
│   ├── value_objects/
│   │   ├── priority.py          # Eisenhower matrix (all contexts)
│   │   ├── deadline.py          # Deadline parsing (all contexts)
│   │   └── duration.py          # Time duration (all contexts)
│   └── types.py                 # Common types
│
├── inventum/                    # Inventum Context
│   ├── entities/
│   │   ├── repair_task.py
│   │   └── client.py
│   ├── services/
│   │   └── repair_service.py
│   └── rules/
│       └── repair_rules.py
│
├── lab/                         # Lab Context
│   ├── entities/
│   │   ├── production_task.py
│   │   └── dental_item.py
│   └── services/
│       └── production_service.py
│
├── rd/                          # R&D Context
│   ├── entities/
│   │   ├── prototype_task.py
│   │   └── prototype.py
│   └── services/
│       └── prototype_service.py
│
└── trade/                       # Trade Context
    ├── entities/
    │   ├── import_task.py
    │   └── supplier.py
    └── services/
        └── import_service.py
```

### Context Enum
```python
from enum import IntEnum

class BusinessContext(IntEnum):
    """The 4 bounded contexts (maps to business_id)."""
    
    INVENTUM = 1  # Dental equipment repair
    LAB = 2       # Dental laboratory
    R_D = 3       # Research & Development
    TRADE = 4     # Import & Trade
    
    @property
    def display_name(self) -> str:
        names = {
            BusinessContext.INVENTUM: "Inventum",
            BusinessContext.LAB: "Inventum Lab",
            BusinessContext.R_D: "R&D",
            BusinessContext.TRADE: "Import & Trade"
        }
        return names[self]
    
    @property
    def keywords(self) -> list[str]:
        """Keywords for AI detection."""
        return CONTEXT_KEYWORDS[self]
```

---

## 🔄 Context Transitions

### No Automatic Transitions
- Tasks don't move between contexts
- Each task has ONE context forever
- If context is wrong, user creates new task

### Cross-Context Workflows

**Example**: Equipment imported (Trade) → Needs repair setup (Inventum)

```python
# ❌ WRONG: Move task between contexts
trade_task.business_context = INVENTUM  # Violates isolation!

# ✅ CORRECT: Create new task in target context
inventum_task = create_task(
    title="Настроить новое оборудование из Китая",
    business_context=INVENTUM,
    related_to=trade_task.id  # Optional link
)
```

---

## 🧪 Testing Context Isolation

```python
async def test_context_isolation():
    """Verify contexts stay isolated."""
    
    # Create similar tasks in different contexts
    inventum_task = await create_task(
        "Диагностика фрезера",
        context=BusinessContext.INVENTUM
    )
    
    rd_task = await create_task(
        "Диагностика прототипа",
        context=BusinessContext.R_D
    )
    
    # Search within Inventum context
    inventum_similar = await find_similar_tasks(
        inventum_task, 
        context=BusinessContext.INVENTUM
    )
    
    # Verify: Only Inventum tasks returned
    for task in inventum_similar:
        assert task.business_context == BusinessContext.INVENTUM
        # Should NOT find "Диагностика прототипа" (R&D context)


async def test_cross_context_member():
    """Test cross-functional member (Максим) works in multiple contexts."""
    
    # Максим in Inventum context
    inventum_task = await create_task(
        "Управленческая задача",
        context=BusinessContext.INVENTUM,
        assigned_to="Максим"
    )
    
    # Максим in R&D context (same person, different context)
    rd_task = await create_task(
        "Разработать прототип",
        context=BusinessContext.R_D,
        assigned_to="Максим"
    )
    
    # Both valid, but tasks stay in their contexts
    assert inventum_task.business_context == BusinessContext.INVENTUM
    assert rd_task.business_context == BusinessContext.R_D
```

---

## 📊 Context Statistics

### Task Distribution (Expected)

| Context | Tasks/Month | % Total | Avg Duration |
|---------|-------------|---------|--------------|
| **Inventum** | ~200 | 40% | 2 hours |
| **Lab** | ~150 | 30% | 1.5 hours |
| **R&D** | ~75 | 15% | 4 hours |
| **Trade** | ~75 | 15% | 1 hour |
| **Total** | 500 | 100% | 2 hours |

### Team Distribution

| Member | Contexts | Tasks/Month |
|--------|----------|-------------|
| Константин | All 4 | ~50 |
| Максим | Inventum, R&D | ~80 |
| Дима | Inventum, R&D | ~100 |
| Максут | Inventum | ~70 |
| Юрий Вл. | Lab | ~50 |
| Мария | Lab | ~100 |
| Слава | Trade | ~75 |
| Лиза | All 4 | ~50 |

---

## 🎯 Success Criteria

Context isolation is successful if:

- [ ] RAG never returns cross-context tasks
- [ ] AI correctly detects context > 90% of time
- [ ] Time estimates accurate within context
- [ ] Analytics make sense per context
- [ ] No "wrong context" user complaints

---

## 📖 References

- Eric Evans - Domain-Driven Design (Bounded Contexts chapter)
- ADR-003: Business Context Isolation
- Database: `docs/02-database/schema.sql` (business_id column)
- Team: `docs/TEAM.md` (cross-functional members)

---

**Status**: ✅ Bounded Contexts Defined  
**Total Contexts**: 4 (Inventum, Lab, R&D, Trade)  
**Critical Principle**: Same words, different meanings across contexts  
**Next**: Define Entities within each context

