# 👥 Team Structure - Business Planner

> **Complete team information for all 4 businesses**  
> **Updated**: 2025-10-17  
> **Total Team Size**: 8 people

---

## 🎯 Leadership

### Константин - CEO
- **Role**: Chief Executive Officer
- **Scope**: Управляет всеми 4 бизнесами
- **Responsibilities**:
  - Strategic decisions across all businesses
  - Overall business management
  - Primary user of Business Planner system
- **Location**: Almaty, Kazakhstan
- **Timezone**: UTC+5
- **Involvement**: All 4 businesses

### Лиза - Маркетинг/SMM
- **Role**: Marketing & Social Media Manager
- **Scope**: Работает со всеми бизнесами
- **Responsibilities**:
  - Marketing strategy
  - Social media management
  - Content creation
  - Brand management
- **Involvement**: All 4 businesses

---

## 🏢 Business 1: Inventum (Dental Equipment Repair)

### Team Structure

#### Максим - Директор
- **Role**: Director of Inventum
- **Responsibilities**:
  - Managing repair operations
  - Client relationships
  - Team coordination
  - Also participates in R&D projects
- **Skills**: Management, diagnostics
- **Cross-functional**: Also in R&D

#### Дима - Мастер
- **Role**: Master Technician
- **Responsibilities**:
  - Equipment repairs
  - Technical diagnostics
  - Workshop operations
  - Also participates in R&D projects
- **Skills**: Technical repairs, problem-solving
- **Cross-functional**: Also in R&D

#### Максут - Выездной мастер
- **Role**: Field Service Technician
- **Responsibilities**:
  - On-site client visits
  - Field repairs and diagnostics
  - Emergency services
  - Client support
- **Skills**: Mobile repairs, customer service

---

## 🦷 Business 2: Inventum Lab (Dental Laboratory)

### Team Structure

#### Юрий Владимирович - Директор
- **Role**: Director of Inventum Lab
- **Responsibilities**:
  - Laboratory operations management
  - Quality control
  - Client relationships
  - Production planning
- **Skills**: Management, dental technology

#### Мария - CAD/CAM оператор
- **Role**: CAD/CAM Operator
- **Responsibilities**:
  - Digital modeling (CAD)
  - CNC milling operations (CAM)
  - Crown and prosthetics production
  - Technical design
- **Skills**: CAD/CAM software, dental modeling
- **Tools**: Dental CAD software, milling machines

---

## 🔬 Business 3: R&D (Research & Development)

### Team Structure

#### Core Team
R&D is a cross-functional team with members from Inventum:

**Максим** (from Inventum)
- Brings management and strategic perspective
- Technical expertise in dental equipment

**Дима** (from Inventum)
- Hands-on technical development
- Prototyping and testing

### Focus
- **Location**: Workshop
- **Projects**: Prototype development
- **Activities**: Design, testing, documentation
- **Innovation**: New equipment and solutions

---

## 💼 Business 4: Import & Trade (Equipment Import)

### Team Structure

#### Слава - Юрист/бухгалтер
- **Role**: Legal & Accounting Specialist
- **Responsibilities**:
  - Legal documentation
  - Customs procedures
  - Accounting and finances
  - Supplier contracts
  - Regulatory compliance
- **Skills**: Legal, accounting, international trade
- **Focus**: Import from China

---

## 📊 Team Overview

### By Business

| Business | Team Members | Headcount |
|----------|--------------|-----------|
| **Leadership** | Константин (CEO), Лиза (Marketing) | 2 |
| **Inventum** | Максим, Дима, Максут | 3 |
| **Inventum Lab** | Юрий Владимирович, Мария | 2 |
| **R&D** | Максим*, Дима* | 2* |
| **Import & Trade** | Слава | 1 |
| **Total Unique** | - | **8 people** |

*\*Cross-functional roles - same people as in Inventum*

### By Role Type

| Role Type | Count |
|-----------|-------|
| **Management** | 3 (CEO + 2 Directors) |
| **Technical** | 3 (Мастер, CAD/CAM, Выездной) |
| **Support** | 2 (Marketing, Legal/Accounting) |

### Cross-Functional Involvement

```
Константин ──┬── Inventum
             ├── Inventum Lab
             ├── R&D
             └── Import & Trade

Лиза ────────┬── Inventum
             ├── Inventum Lab
             ├── R&D
             └── Import & Trade

Максим ──────┬── Inventum (Director)
             └── R&D (Participant)

Дима ────────┬── Inventum (Master)
             └── R&D (Participant)
```

---

## 🎯 Task Assignment Logic

### Automatic Assignment Rules

When creating tasks, the system should suggest team members based on:

#### For Inventum (@inventum)
- **Repairs, diagnostics**: Дима, Максут
- **Management, planning**: Максим
- **Client visits**: Максут (if on-site)
- **Workshop repairs**: Дима

#### For Inventum Lab (@lab)
- **CAD/CAM work, modeling**: Мария
- **Management, planning**: Юрий Владимирович
- **Production tasks**: Мария
- **Quality control**: Юрий Владимирович

#### For R&D (@r&d)
- **All tasks**: Максим, Дима
- **Design tasks**: Both
- **Testing tasks**: Both
- **Documentation**: Both

#### For Import & Trade (@trade)
- **Legal, contracts**: Слава
- **Customs, documentation**: Слава
- **Accounting**: Слава
- **Supplier coordination**: Слава (with Константин)

#### Cross-Business
- **Marketing, SMM**: Лиза (any business)
- **Strategic decisions**: Константин (any business)

---

## 💡 Important Notes for System Design

### Database Structure

#### Members Table
```sql
CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(200),
    businesses TEXT[], -- Array of business IDs
    skills TEXT[],
    is_cross_functional BOOLEAN DEFAULT FALSE
);
```

#### Example Data
```sql
INSERT INTO members VALUES
  ('Константин', 'CEO', ['inventum', 'lab', 'r&d', 'trade'], ['management'], true),
  ('Максим', 'Директор Inventum', ['inventum', 'r&d'], ['management', 'diagnostics'], true),
  ('Дима', 'Мастер', ['inventum', 'r&d'], ['repairs', 'technical'], true),
  ('Максут', 'Выездной мастер', ['inventum'], ['field_service', 'repairs'], false),
  ('Юрий Владимирович', 'Директор Inventum Lab', ['lab'], ['management', 'quality'], false),
  ('Мария', 'CAD/CAM оператор', ['lab'], ['cad', 'cam', 'modeling'], false),
  ('Слава', 'Юрист/бухгалтер', ['trade'], ['legal', 'accounting'], false),
  ('Лиза', 'Маркетинг/SMM', ['inventum', 'lab', 'r&d', 'trade'], ['marketing', 'smm'], true);
```

### Task Assignment AI Prompt

When parsing voice tasks, GPT-5 Nano should:

1. **Detect business context** (inventum, lab, r&d, trade)
2. **Identify task type** (repair, modeling, legal, marketing, etc.)
3. **Suggest appropriate team member(s)** based on:
   - Business context
   - Task type
   - Member skills
   - Cross-functional roles

Example:
```
Voice: "Дима должен сделать диагностику платы для Иванова"
→ Business: Inventum
→ Assignee: Дима (Мастер Inventum)
→ Task type: diagnostics

Voice: "Нужно смоделировать коронку для клиента"
→ Business: Inventum Lab
→ Assignee: Мария (CAD/CAM оператор)
→ Task type: modeling
```

---

## 🔍 Search & Filter Logic

### By Business
- **Inventum tasks**: Can assign to Максим, Дима, Максут (+ Константин, Лиза)
- **Lab tasks**: Can assign to Юрий Владимирович, Мария (+ Константин, Лиза)
- **R&D tasks**: Can assign to Максим, Дима (+ Константин)
- **Trade tasks**: Can assign to Слава (+ Константин, Лиза)

### By Person
- **Максим's tasks**: From Inventum + R&D
- **Дима's tasks**: From Inventum + R&D
- **Лиза's tasks**: From all businesses
- **Константин's tasks**: From all businesses
- **Others**: From their specific business

---

## 📝 Example Task Assignments

### Scenario 1: Repair Task
```
Voice: "Завтра Дима должен починить фрезер для Иванова"
→ Business: Inventum
→ Assignee: Дима
→ Title: Починить фрезер для Иванова
→ Deadline: Tomorrow
```

### Scenario 2: CAD Work
```
Voice: "Мария, нужно смоделировать 3 коронки к пятнице"
→ Business: Inventum Lab
→ Assignee: Мария
→ Title: Смоделировать 3 коронки
→ Deadline: Friday
```

### Scenario 3: Legal Task
```
Voice: "Слава должен подготовить контракт с новым поставщиком"
→ Business: Import & Trade
→ Assignee: Слава
→ Title: Подготовить контракт с новым поставщиком
```

### Scenario 4: Marketing Task
```
Voice: "Лиза, нужен пост в инстаграм про новые услуги лаборатории"
→ Business: Inventum Lab
→ Assignee: Лиза
→ Title: Пост в Instagram про новые услуги
```

### Scenario 5: R&D Task
```
Voice: "Максим и Дима, разработайте прототип нового наконечника"
→ Business: R&D
→ Assignees: Максим, Дима
→ Title: Разработать прототип нового наконечника
```

---

## 🎯 Key Takeaways for Development

1. **8 unique people** total across 4 businesses
2. **2 cross-business roles**: Константин (CEO), Лиза (Marketing)
3. **2 cross-functional**: Максим and Дима (Inventum + R&D)
4. **Task assignment** should be context-aware
5. **Business isolation** still applies for task context
6. **Team member suggestions** help user delegate tasks quickly

---

**Last Updated**: 2025-10-17  
**For**: Business Planner Project  
**Use**: Reference for AI task assignment and team management features



