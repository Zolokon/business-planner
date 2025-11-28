# Claude Context - Business Planner

## Проект
Voice-first планировщик задач для CEO с 4 бизнесами (Inventum, Inventum Lab, R&D, Trade).
Продакшн: https://inventum.kz

## Стек
- FastAPI + LangGraph + PostgreSQL + pgvector
- Telegram Bot (python-telegram-bot)
- OpenAI Whisper (транскрипция) + GPT-4o-mini (парсинг)
- APScheduler (ежедневные сводки в 7:00 и 19:00)

## Ключевые файлы
- `src/ai/graphs/voice_task_creation.py` - LangGraph workflow голос→задача
- `src/ai/parsers/task_parser.py` - GPT парсер транскрипта
- `src/telegram/handlers/voice_handler.py` - обработчик голосовых
- `src/telegram/handlers/callback_handler.py` - inline кнопки
- `src/telegram/handlers/message_handler.py` - текстовые сообщения
- `src/services/scheduler.py` - расписание сводок
- `src/services/daily_summary.py` - утренняя сводка
- `src/services/evening_summary.py` - вечерняя сводка
- `src/domain/constants.py` - BUSINESS_NAMES, PRIORITY_CIRCLES, PRIORITY_NAMES
- `src/infrastructure/database/repositories/task_repository.py` - репозиторий задач

## Последние изменения (Session 11)

### Реализовано: Редактирование транскрипта
Пользователь может исправить текстовую расшифровку голоса и задача перепарсится.

**Изменённые файлы:**
1. `src/domain/models/task.py:101-104` - добавлено поле `task_metadata` в TaskCreate
2. `src/ai/graphs/voice_task_creation.py:274-288` - сохранение транскрипта в metadata
3. `src/infrastructure/database/repositories/task_repository.py:421-458` - методы get_metadata(), update_metadata()
4. `src/telegram/handlers/callback_handler.py:225-237` - кнопка "Текст" в меню редактирования
5. `src/telegram/handlers/callback_handler.py:267-320` - handle_edit_transcript_callback()
6. `src/telegram/handlers/message_handler.py:103-227` - handle_transcript_update() с перепарсингом

**Флоу:**
1. Голос → транскрипт сохраняется в task_metadata
2. Кнопка "Изменить" → меню с кнопкой "Текст"
3. "Текст" → показ текущего транскрипта
4. Отправка исправления → AI перепарсит → обновление задачи

### Предыдущие изменения (Session 10)
- Время утренней сводки: 8:00 → 7:00
- Сводка не отправляется если нет задач
- Общие константы в `src/domain/constants.py`

## Не закоммичено
Все изменения Session 11 (редактирование транскрипта) ещё не закоммичены.

## Команды
```bash
# Запуск локально
docker-compose up -d  # PostgreSQL + Redis
python -m uvicorn src.main:app --reload

# Деплой
ssh root@...
cd /opt/business-planner && git pull && docker-compose -f docker-compose.prod.yml up -d --build
```
