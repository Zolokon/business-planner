# Monitoring & Logging Strategy - Business Planner

> **Observability and alerting**  
> **Created**: 2025-10-17  
> **Reference**: .cursorrules (Logging Strategy)

---

## 🎯 Monitoring Goals

1. **Detect issues** before user notices
2. **Track performance** (response times, errors)
3. **Understand usage** (patterns, costs)
4. **Debug problems** quickly

---

## 📊 Three-Level Monitoring

### Level 1: Infrastructure (Digital Ocean)

**Free DO Monitoring**:
- CPU usage
- Memory usage
- Disk usage
- Bandwidth
- Load average

**Alerts** (email or webhook):
```
CPU > 80% for 5 minutes
Memory > 90%
Disk > 80%
Droplet unreachable
```

---

### Level 2: Application (Structured Logging)

**Framework**: structlog (Python)

**Log Format**: JSON for easy parsing

```python
import structlog

logger = structlog.get_logger()

# Example log
logger.info(
    "task_created",
    task_id=123,
    user_id=1,
    business_id=1,
    title="Починить фрезер",
    estimated_duration=120,
    created_via="voice",
    processing_time_ms=4500
)

# Output (JSON):
{
  "event": "task_created",
  "task_id": 123,
  "user_id": 1,
  "business_id": 1,
  "title": "Починить фрезер",
  "estimated_duration": 120,
  "created_via": "voice",
  "processing_time_ms": 4500,
  "timestamp": "2025-10-17T15:30:45.123Z",
  "level": "info"
}
```

---

### Level 3: AI/Business Metrics (Custom)

**Track**:
- Tasks created per day
- Voice vs text ratio
- Business distribution
- Time estimation accuracy
- AI API costs
- Processing times

```python
# Example metric
logger.info(
    "daily_metrics",
    date="2025-10-17",
    tasks_created=12,
    voice_messages=10,
    text_messages=2,
    avg_processing_time_ms=4200,
    ai_cost_usd=0.05
)
```

---

## 📝 Logging Configuration

### Debug Mode Toggle

**User Preference** [[memory:7583598]]: Serial output only in debug mode

```python
import os
import structlog

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

if DEBUG:
    # Development: Colorful console
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()  # Colorful, readable
        ]
    )
else:
    # Production: JSON to file
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()  # JSON for parsing
        ]
    )
```

---

### Log Levels

```python
# DEBUG: Detailed (only in debug mode)
logger.debug("detailed_info", sql_query=query, params=params)

# INFO: Normal operations
logger.info("task_created", task_id=123)

# WARNING: Potentially problematic
logger.warning("slow_query", duration_ms=2000, query="SELECT ...")

# ERROR: Errors that need attention
logger.error("ai_api_failed", error=str(e), model="gpt-5-nano")

# CRITICAL: System-critical errors
logger.critical("database_connection_lost", details=str(e))
```

---

### Log Rotation

```yaml
# Docker logging (docker-compose.prod.yml)
logging:
  driver: "json-file"
  options:
    max-size: "50m"
    max-file: "5"

# Total: 50MB × 5 = 250MB per service
```

**Additional**: logrotate for application logs

```
/var/log/planner/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

---

## 📈 Metrics to Track

### Application Metrics

| Metric | Alert Threshold |
|--------|-----------------|
| **Request rate** | - |
| **Response time (p95)** | > 5s |
| **Error rate** | > 5% |
| **Task creation rate** | < 5/day (unusual) |
| **Voice processing time** | > 15s |

### Infrastructure Metrics

| Metric | Alert Threshold |
|--------|-----------------|
| **CPU usage** | > 80% for 5 min |
| **Memory usage** | > 90% |
| **Disk usage** | > 80% |
| **Docker containers** | Any unhealthy |

### Business Metrics

| Metric | Alert Threshold |
|--------|-----------------|
| **AI API cost/day** | > $0.50 |
| **Estimation accuracy** | < 60% (after 1 month) |
| **Telegram errors** | > 3 per day |
| **Tasks per day** | < 5 (user not using) |

---

## 🔔 Alerting

### Alert Channels

**Primary**: Telegram (same bot!)
```python
async def send_alert(message: str, severity: str):
    """Send alert to admin via Telegram."""
    
    emoji = {
        "critical": "🚨",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️"
    }
    
    await bot.send_message(
        chat_id=ADMIN_CHAT_ID,  # Константин
        text=f"{emoji[severity]} {message}"
    )
```

**Secondary**: Email (optional)

---

### Alert Examples

```
🚨 CRITICAL: Database connection lost
Action: Check docker-compose logs -f postgres

❌ ERROR: AI API rate limit exceeded
Action: Check OPENAI_API_KEY quota

⚠️ WARNING: Memory usage 92%
Action: Consider upgrading Droplet

ℹ️ INFO: 20 tasks created today (high activity)
Action: None (informational)
```

---

## 📊 Dashboards (Optional)

### Simple: Grafana + Prometheus

**If needed in future**:

```yaml
# Add to docker-compose.prod.yml
prometheus:
  image: prom/prometheus:latest
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana:latest
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=secure_password
```

**Cost**: $0 (runs on same Droplet)  
**RAM**: +100MB  
**When**: Only if need visual dashboards

---

## 📝 Log Analysis

### Daily Log Review

```bash
# SSH to Droplet
ssh planner@droplet-ip

# View backend logs (last 100 lines)
docker logs --tail 100 planner_backend

# Search for errors
docker logs planner_backend | grep ERROR

# Filter by level
docker logs planner_backend | grep '"level":"error"'

# View specific time range
docker logs planner_backend --since 2h --until 1h
```

### Log Aggregation (Optional)

For future (if needed):
- Loki + Grafana (log aggregation)
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Cloud service (Papertrail, Loggly)

**Current**: Docker logs sufficient for 1 user

---

## 🔍 Health Checks

### Endpoint: /health

```python
@app.get("/health")
async def health_check():
    """System health check."""
    
    checks = {}
    
    # Database
    try:
        await db.execute("SELECT 1")
        checks["database"] = True
    except Exception as e:
        checks["database"] = False
        logger.error("health_check_db_failed", error=str(e))
    
    # Redis
    try:
        await redis.ping()
        checks["redis"] = True
    except Exception:
        checks["redis"] = False
    
    # OpenAI API
    try:
        # Quick API check (or cached result)
        checks["openai_api"] = await check_openai_health()
    except Exception:
        checks["openai_api"] = False
    
    # Overall status
    all_healthy = all(checks.values())
    
    if all_healthy:
        return {"status": "healthy", "checks": checks}
    else:
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "checks": checks}
        )
```

**Monitored by**:
- Docker health check
- External monitoring (UptimeRobot)
- DO monitoring

---

## 📖 References

- structlog: https://www.structlog.org/
- Prometheus: https://prometheus.io/
- .cursorrules (Logging Strategy section)
- User Preference: [[memory:7583598]] Debug mode toggle

---

**Status**: ✅ Monitoring Strategy Complete  
**Levels**: 3 (Infrastructure, Application, Business)  
**Alerting**: Telegram-first  
**Debug Mode**: Configurable via DEBUG env var  
**Next**: Security & Secrets Management

