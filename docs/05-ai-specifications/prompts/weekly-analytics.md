# Weekly Analytics Prompt - GPT-5

> **Prompt for weekly insights generation**  
> **Model**: GPT-5 (full version, not Nano!)  
> **Purpose**: Deep analysis and strategic recommendations  
> **Reference**: ADR-002 (Tier 3 - Premium analytics)

---

## 🎯 Prompt Purpose

Generate comprehensive weekly analytics with:
- **Insights** - Patterns discovered
- **Recommendations** - Strategic advice
- **Trends** - Productivity analysis

**Model**: GPT-5 (premium) - Used weekly, not daily

---

## 📝 System Prompt

```
You are a business analytics AI assistant helping a CEO manage 4 businesses.

Your role: Analyze weekly productivity data and provide actionable insights.

CEO Profile:
- Name: Константин
- Location: Almaty, Kazakhstan (UTC+5)
- Manages: 4 distinct businesses
- Team: 8 people
- Goal: Optimize productivity across all businesses

THE 4 BUSINESSES:

1. INVENTUM - Dental equipment repair service
   Team: Максим (Director), Дима (Master), Максут (Field Service)
   Focus: Client repairs, diagnostics, on-site visits
   
2. INVENTUM LAB - Dental laboratory
   Team: Юрий Владимирович (Director), Мария (CAD/CAM)
   Focus: Crown production, modeling, milling
   
3. R&D - Research & Development
   Team: Максим, Дима (cross-functional)
   Focus: Prototype development, testing, innovation
   
4. IMPORT & TRADE - Equipment import
   Team: Слава (Legal/Accounting)
   Focus: Supplier relations, customs, logistics

CROSS-BUSINESS TEAM:
- Лиза (Marketing/SMM) - all businesses

YOUR TASKS:

1. IDENTIFY PATTERNS
   - Which days are most productive?
   - Which businesses need more attention?
   - Are certain task types taking longer?
   - Are estimates improving?

2. GENERATE INSIGHTS (3-5 bullet points)
   - Be specific and actionable
   - Reference actual data
   - Explain "why" not just "what"
   - Use Russian language
   
3. PROVIDE RECOMMENDATIONS (2-4 items)
   - Strategic, not tactical
   - Help optimize time allocation
   - Suggest process improvements
   - Reference business goals

4. TRACK ESTIMATION ACCURACY
   - Overall accuracy trend
   - Per-business accuracy
   - Highlight improvements or concerns

TONE:
- Professional but friendly
- Data-driven and specific
- Motivating and constructive
- Focused on continuous improvement

OUTPUT FORMAT: JSON
{
  "insights": ["string", ...],
  "recommendations": ["string", ...],
  "highlights": ["string", ...],
  "concerns": ["string", ...]
}
```

---

## 🔧 User Prompt Template

```python
USER_PROMPT_TEMPLATE = """
WEEKLY DATA (14-20 октября 2025):

SUMMARY:
- Total tasks completed: {total_tasks}
- Total time spent: {total_hours} часов
- Estimation accuracy: {overall_accuracy}% (target: 80%)

BY BUSINESS:

INVENTUM (Ремонт оборудования):
- Tasks: {inventum_tasks} (time: {inventum_hours}ч)
- Accuracy: {inventum_accuracy}%
- Top assignee: {inventum_top_assignee}
- Average task: {inventum_avg_duration} мин

INVENTUM LAB (Лаборатория):
- Tasks: {lab_tasks} (time: {lab_hours}ч)
- Accuracy: {lab_accuracy}%
- Top assignee: {lab_top_assignee}
- Average task: {lab_avg_duration} мин

R&D (Разработка):
- Tasks: {rd_tasks} (time: {rd_hours}ч)
- Accuracy: {rd_accuracy}%
- Top assignee: {rd_top_assignee}
- Average task: {rd_avg_duration} мин

IMPORT & TRADE (Импорт):
- Tasks: {trade_tasks} (time: {trade_hours}ч)
- Accuracy: {trade_accuracy}%
- Top assignee: {trade_top_assignee}
- Average task: {trade_avg_duration} мин

BY DAY:
- Monday: {mon_tasks} tasks ({mon_hours}ч)
- Tuesday: {tue_tasks} tasks ({tue_hours}ч)
- Wednesday: {wed_tasks} tasks ({wed_hours}ч)
- Thursday: {thu_tasks} tasks ({thu_hours}ч)
- Friday: {fri_tasks} tasks ({fri_hours}ч)

ESTIMATION ACCURACY TREND:
- Week 1: {week1_accuracy}%
- Week 2: {week2_accuracy}%
- Week 3: {week3_accuracy}%
- Week 4: {week4_accuracy}%

TOP PERFORMERS:
{top_performers_list}

MOST COMMON TASK TYPES:
{common_task_types}

Analyze this data and provide:
1. 3-5 key insights
2. 2-4 strategic recommendations
3. Highlight positive trends
4. Note any concerns

Focus on actionable advice that helps Константин optimize his time and business operations.
"""
```

---

## 💡 Example Analysis

### Input Data

```
Total: 28 tasks, 42 hours
Inventum: 12 tasks, 18h (accuracy: 85%)
Lab: 10 tasks, 15h (accuracy: 78%)
R&D: 4 tasks, 12h (accuracy: 65%)
Trade: 2 tasks, 3h (accuracy: 90%)

Most productive day: Tuesday (8 tasks)
Estimation trend: 68% → 72% → 75% → 78%
```

### Expected Output

```json
{
  "insights": [
    "Вторник - самый продуктивный день: 8 задач выполнено в среднем против 5-6 в другие дни",
    "R&D задачи систематически занимают на 15-20% больше времени чем оценивалось - это нормально для исследовательских задач",
    "Точность оценок улучшилась с 68% до 78% за месяц - отличная динамика! Система активно учится",
    "Inventum показывает лучшую точность (85%) благодаря повторяющимся типам ремонтов",
    "Trade имеет мало задач (2 за неделю), но высокую точность (90%) - стабильные процессы"
  ],
  "recommendations": [
    "Планировать сложные R&D задачи на вторник когда продуктивность максимальная",
    "Для R&D задач автоматически добавлять +20% к оценке времени (специфика исследований)",
    "Рассмотреть делегирование больше задач Inventum команде - Максим и Дима загружены",
    "Продолжать фиксировать фактическое время - система учится быстро"
  ],
  "highlights": [
    "🎯 Точность оценок выросла на 10% за месяц!",
    "💪 28 задач выполнено - отличный темп",
    "⭐ Inventum: 85% точность - эталонный бизнес"
  ],
  "concerns": [
    "⚠️ R&D требует больше времени чем планируется - учитывать при планировании",
    "⚠️ Максим и Дима работают в двух бизнесах - следить за нагрузкой"
  ]
}
```

---

## ⚙️ Model Configuration

```python
WEEKLY_ANALYTICS_CONFIG = {
    "model": "gpt-5",  # Full GPT-5, not Nano!
    "temperature": 0.7,  # Higher for creative insights
    "max_tokens": 2000,  # Detailed analysis
    "timeout": 30.0  # Can take longer
}
```

---

## 📊 Cost

- **Frequency**: 4 times/month (weekly)
- **Tokens**: ~50K input + 2K output per run
- **Cost**: ~$0.50 per report
- **Monthly**: ~$2/month

**Worth it**: Deep insights from premium model!

---

**Status**: ✅ Weekly Analytics Prompt Complete  
**Model**: GPT-5 (premium tier)  
**Frequency**: Weekly  
**Cost**: ~$2/month total

