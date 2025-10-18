# Security Strategy - Business Planner

> **Security best practices and secrets management**  
> **Created**: 2025-10-17  
> **Priority**: High (handles business data)

---

## 🔒 Security Layers

### Defense in Depth

```
1. Network Security (Firewall)
   ↓
2. SSL/TLS Encryption (HTTPS)
   ↓
3. Application Security (Input validation)
   ↓
4. Database Security (Constraints, permissions)
   ↓
5. Secrets Management (Environment variables)
```

---

## 🛡️ 1. Network Security

### Digital Ocean Firewall

```hcl
# Only allow necessary ports
Inbound:
  - SSH (22) - Restricted to your IP only
  - HTTP (80) - Redirect to HTTPS
  - HTTPS (443) - Public

Outbound:
  - All (for API calls)
```

### SSH Hardening

```bash
# /etc/ssh/sshd_config
PermitRootLogin no               # Disable root login
PasswordAuthentication no        # Key-only authentication
PubkeyAuthentication yes
UsePAM no
AllowUsers planner               # Only specific user

# Restart SSH
systemctl restart sshd
```

### Fail2Ban

```bash
# Auto-ban brute force attempts

# /etc/fail2ban/jail.local
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600      # Ban for 1 hour
findtime = 600      # 3 failures in 10 minutes

# Start
systemctl enable fail2ban
systemctl start fail2ban
```

---

## 🔐 2. SSL/TLS (HTTPS)

### Let's Encrypt (Free)

```bash
# Install Certbot
apt-get install certbot python3-certbot-nginx

# Obtain certificate
certbot --nginx \
  -d planner.yourdomain.com \
  --email konstantin@example.com \
  --agree-tos \
  --non-interactive

# Auto-renewal (systemd timer)
systemctl list-timers | grep certbot
# Runs twice daily, renews if < 30 days left
```

### SSL Configuration (A+ Rating)

```nginx
# nginx.conf
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# HSTS (force HTTPS)
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

**Test**: https://www.ssllabs.com/ssltest/

---

## 🔑 3. Secrets Management

### Environment Variables (NOT in Code!)

```python
# ✅ GOOD
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ❌ BAD
OPENAI_API_KEY = "sk-xxxxxxxxxxxxx"  # NEVER!
```

### .env File (Production)

```bash
# On Droplet: /opt/business-planner/.env
# Permissions: 600 (only owner can read)

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Telegram
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_SECRET_TOKEN=random-secret-string-for-validation

# Database
DB_PASSWORD=secure_random_password_here

# Application
SECRET_KEY=another-random-key-for-sessions
WEBHOOK_URL=https://planner.yourdomain.com/webhook/telegram
```

**Create securely**:
```bash
# Generate random passwords
openssl rand -base64 32

# Set restrictive permissions
chmod 600 .env
chown planner:planner .env
```

### Never Commit Secrets!

```.gitignore
# NEVER commit these
.env
.env.local
.env.production
*.pem
*.key
secrets/
```

---

## 🔐 4. Application Security

### Input Validation (Pydantic)

```python
# All inputs validated automatically
@app.post("/tasks")
async def create_task(task_data: TaskCreate):  # ← Pydantic validates
    # If we're here, input is valid ✅
    ...
```

### SQL Injection Prevention

```python
# ✅ GOOD: SQLAlchemy (parameterized)
stmt = select(Task).where(Task.id == task_id)
result = await session.execute(stmt)

# ❌ BAD: String interpolation
query = f"SELECT * FROM tasks WHERE id = {task_id}"  # NEVER!
```

### XSS Prevention

```python
# For Telegram: Escape HTML
import html

safe_text = html.escape(user_input)
await bot.send_message(text=safe_text, parse_mode='HTML')
```

### Rate Limiting

```python
from slowapi import Limiter

limiter = Limiter(key_func=lambda: request.client.host)

@app.post("/webhook/telegram")
@limiter.limit("30/minute")
async def telegram_webhook(request: Request):
    ...
```

---

## 🔐 5. Telegram Security

### Webhook Signature Validation

```python
import hmac
import hashlib

def validate_telegram_request(request: Request) -> bool:
    """Verify request is from Telegram."""
    
    # Secret token
    secret = os.getenv("TELEGRAM_SECRET_TOKEN")
    
    # Header from Telegram
    received_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    
    if not received_token:
        return False
    
    # Constant-time comparison (prevent timing attacks)
    return hmac.compare_digest(received_token, secret)


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    # Validate first!
    if not validate_telegram_request(request):
        logger.warning("Invalid Telegram signature", ip=request.client.host)
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Process...
```

---

## 🗄️ 6. Database Security

### Least Privilege Principle

```sql
-- Create app user (not superuser)
CREATE USER planner_app WITH PASSWORD 'secure_password';

-- Grant only necessary permissions
GRANT CONNECT ON DATABASE planner TO planner_app;
GRANT USAGE ON SCHEMA public TO planner_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO planner_app;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO planner_app;

-- NO DROP, NO TRUNCATE, NO ALTER
```

### Connection String Security

```python
# ✅ GOOD: From environment
DATABASE_URL = os.getenv("DATABASE_URL")

# ❌ BAD: Hardcoded
DATABASE_URL = "postgresql://planner:password@localhost/planner"
```

### Sensitive Data

```python
# Mask sensitive data in logs
logger.info(
    "user_activity",
    user_id=user.id,
    telegram_id="***MASKED***",  # Don't log
    api_key="***MASKED***"       # Don't log
)
```

---

## 🔐 7. Secrets Checklist

### What to Keep Secret

- ✅ **OPENAI_API_KEY** - AI API access
- ✅ **TELEGRAM_BOT_TOKEN** - Bot authentication
- ✅ **TELEGRAM_SECRET_TOKEN** - Webhook validation
- ✅ **DB_PASSWORD** - Database password
- ✅ **SECRET_KEY** - Application secret
- ✅ **SSH_PRIVATE_KEY** - Server access

### What's OK to Commit

- ✅ `.env.example` - Template without values
- ✅ `docker-compose.yml` - Uses env vars
- ✅ Public configuration
- ✅ Documentation

---

## 🔍 Security Audit Checklist

### Before Production

- [ ] No secrets in code
- [ ] No secrets in Git history
- [ ] .env has restrictive permissions (600)
- [ ] SSH key-only authentication
- [ ] Firewall configured
- [ ] SSL certificate installed
- [ ] Fail2ban running
- [ ] Database user has minimal permissions
- [ ] Rate limiting enabled
- [ ] Telegram signature validation working
- [ ] Health checks configured
- [ ] Backups automated
- [ ] Monitoring alerts set up

---

## 🚨 Incident Response

### If Compromised

1. **Immediate**:
   ```bash
   # Revoke all API keys
   # Rotate all secrets
   # Check audit logs
   ```

2. **Investigation**:
   ```bash
   # Check access logs
   grep "suspicious_ip" /var/log/nginx/access.log
   
   # Check auth attempts
   journalctl -u ssh
   ```

3. **Recovery**:
   ```bash
   # Restore from backup if needed
   # Update all secrets
   # Deploy with new secrets
   ```

---

## 📊 Security Metrics

| Metric | Target |
|--------|--------|
| **Failed SSH attempts** | < 10/day (fail2ban) |
| **Invalid Telegram requests** | < 5/day |
| **SQL injection attempts** | 0 (blocked by ORM) |
| **Secrets in logs** | 0 |
| **Outdated packages** | 0 (weekly updates) |

---

## 📖 References

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Let's Encrypt: https://letsencrypt.org/
- .cursorrules (Security section)

---

**Status**: ✅ Security Strategy Complete  
**Layers**: 7 (defense in depth)  
**Secrets**: Environment variables only  
**SSL**: Let's Encrypt (free, auto-renew)  
**Next**: Testing Strategy

