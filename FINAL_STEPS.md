# 🚀 Финальные шаги до полного запуска

## ✅ Текущий статус

**Готово:**
- ✅ Приложение работает на 164.92.225.137
- ✅ База данных PostgreSQL + pgvector в Docker
- ✅ Systemd service с автоперезапуском
- ✅ Nginx reverse proxy настроен
- ✅ Firewall (порты 80, 443 открыты)
- ✅ Health check: http://164.92.225.137/health

**Осталось 2 шага (~10 минут):**

---

**ТЕКУЩИЙ IP:** 89.35.125.17
**НОВЫЙ IP:** 164.92.225.137

### Инструкция:

1. Зайдите в панель управления доменом inventum.com.kz
2. Найдите DNS записи (DNS Management / DNS Settings)
3. Найдите A-запись (Type: A), которая указывает на 89.35.125.17
4. Измените IP адрес на **164.92.225.137**
5. Сохраните изменения

**Ожидаемое время применения:** 5-30 минут (DNS propagation)

### Проверка DNS:

```bash
# Когда DNS обновится, эта команда покажет новый IP
nslookup inventum.com.kz

# Должно показать:
# Address: 164.92.225.137
```

---

## 📝 Шаг 2: Получить SSL + настроить Telegram webhook

**⚠️ Выполняйте ТОЛЬКО после обновления DNS!**

### Быстрый скрипт (скопируйте и выполните):

```bash
ssh root@164.92.225.137 'bash -s' << '\''ENDSSH'\''

# Цвета для вывода
GREEN='\''\033[0;32m'\''
RED='\''\033[0;31m'\''
NC='\''\033[0m'\''

echo "🔒 Получаем SSL сертификат..."
certbot --nginx -d inventum.com.kz --non-interactive --agree-tos -m konstantin@inventum.com.kz

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ SSL сертификат получен${NC}"
else
    echo -e "${RED}❌ Ошибка получения SSL${NC}"
    exit 1
fi

echo ""
echo "🔗 Настраиваем Telegram webhook..."
WEBHOOK_RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot6732079237:AAG1H2rheoHJVyvDnXF2moKh0yvDkK0Ymdg/setWebhook" \
  -d "url=https://inventum.com.kz/webhook/telegram" \
  -d '\''allowed_updates=["message","callback_query"]'\'')

if echo "$WEBHOOK_RESPONSE" | grep -q '\''"ok":true'\''; then
    echo -e "${GREEN}✅ Telegram webhook настроен${NC}"
    echo "$WEBHOOK_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Ошибка настройки webhook${NC}"
    echo "$WEBHOOK_RESPONSE" | python3 -m json.tool
    exit 1
fi

echo ""
echo "🔍 Проверяем webhook..."
curl -s "https://api.telegram.org/bot6732079237:AAG1H2rheoHJVyvDnXF2moKh0yvDkK0Ymdg/getWebhookInfo" | python3 -m json.tool

echo ""
echo -e "${GREEN}✅ ВСЕ ГОТОВО!${NC}"
echo ""
echo "Следующие шаги:"
echo "1. Откройте Telegram"
echo "2. Найдите вашего бота"
echo "3. Отправьте /start"
echo ""
echo "Логи: tail -f /root/business-planner/app.log"

ENDSSH
```

### Ручная настройка (если скрипт не работает):

```bash
ssh root@164.92.225.137

# 1. Получить SSL сертификат
certbot --nginx -d inventum.com.kz --non-interactive --agree-tos -m konstantin@inventum.com.kz

# 2. Проверить HTTPS
curl https://inventum.com.kz/health

# 3. Настроить Telegram webhook
curl -X POST "https://api.telegram.org/bot6732079237:AAG1H2rheoHJVyvDnXF2moKh0yvDkK0Ymdg/setWebhook" \
  -d "url=https://inventum.com.kz/webhook/telegram" \
  -d 'allowed_updates=["message","callback_query"]'

# 4. Проверить webhook
curl -s "https://api.telegram.org/bot6732079237:AAG1H2rheoHJVyvDnXF2moKh0yvDkK0Ymdg/getWebhookInfo"
```

---

## ✅ Шаг 3: Тестирование

### Проверить бота в Telegram:

1. Найдите бота в Telegram (имя бота из @BotFather)
2. Отправьте команду: `/start`
3. Ожидаемый ответ: приветственное сообщение
4. Попробуйте другие команды:
   - `/today` - задачи на сегодня
   - `/week` - задачи на неделю
   - `/help` - справка

### Проверить логи:

```bash
# Логи приложения
tail -f /root/business-planner/app.log

# Логи systemd
journalctl -u business-planner -f

# Логи Nginx
tail -f /var/log/nginx/business-planner.access.log
```

---

## 🔧 Полезные команды

### Управление сервисом:

```bash
# Статус
systemctl status business-planner

# Перезапуск
systemctl restart business-planner

# Остановка
systemctl stop business-planner

# Логи
journalctl -u business-planner -f
```

### Обновление кода:

```bash
cd /root/business-planner
git pull origin main
systemctl restart business-planner
```

### Проверка здоровья:

```bash
# Health check (после SSL)
curl https://inventum.com.kz/health

# Telegram bot info
curl -s "https://api.telegram.org/bot6732079237:AAG1H2rheoHJVyvDnXF2moKh0yvDkK0Ymdg/getMe"

# Webhook info
curl -s "https://api.telegram.org/bot6732079237:AAG1H2rheoHJVyvDnXF2moKh0yvDkK0Ymdg/getWebhookInfo"
```

### Проверка базы данных:

```bash
docker exec planner_postgres psql -U planner -d planner -c '\dt'
docker exec planner_postgres psql -U planner -d planner -c 'SELECT * FROM businesses;'
docker exec planner_postgres psql -U planner -d planner -c 'SELECT * FROM tasks;'
```

---

## ❗ Troubleshooting

### Бот не отвечает:

1. Проверьте логи: `tail -f /root/business-planner/app.log`
2. Проверьте webhook: `curl -s "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"`
3. Проверьте сервис: `systemctl status business-planner`
4. Проверьте базу: `docker exec planner_postgres psql -U planner -d planner -c '\dt'`

### SSL не работает:

1. Убедитесь, что DNS обновился: `nslookup inventum.com.kz`
2. Проверьте Nginx: `nginx -t && systemctl status nginx`
3. Попробуйте получить сертификат снова: `certbot --nginx -d inventum.com.kz`

### База данных не работает:

```bash
# Проверить контейнеры
docker ps

# Проверить подключение
docker exec planner_postgres psql -U planner -d planner -c 'SELECT 1;'

# Перезапустить контейнеры (если нужно)
cd /root/business-planner
docker-compose -f docker-compose.prod.yml restart
```

### Проверка использования ресурсов:

```bash
# Память
free -h

# Диск
df -h

# Процессы
top
```

---

## 🎉 После успешного запуска

Обновите START_HERE.md, чтобы отметить завершение:

```markdown
### Phase 3: Deployment [████████████████████████████] 100% ✅

**Status:** 🟢 PRODUCTION - Fully Operational

- ✅ Application deployed to Digital Ocean
- ✅ Nginx reverse proxy + SSL configured
- ✅ Telegram webhook configured
- ✅ Bot responding to messages

**Live URL:** https://inventum.com.kz
```

---

**Готово к запуску!** Осталось обновить DNS и выполнить скрипт из Шага 2.
