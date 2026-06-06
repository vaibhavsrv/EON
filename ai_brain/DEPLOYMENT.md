# EON AI Brain - Deployment Guide

## Production Deployment Checklist

### Pre-Deployment

- [ ] Set GROQ_API_KEY in .env
- [ ] Configure allowed hosts/domains in CORS
- [ ] Set up SSL/TLS certificates
- [ ] Create database backup strategy
- [ ] Set up monitoring and logging
- [ ] Configure rate limiting

### Deployment Options

#### 1. Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t eon-brain .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key eon-brain
```

#### 2. Systemd Service

Create `/etc/systemd/system/eon-brain.service`:

```ini
[Unit]
Description=EON AI Brain Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/eon-brain
Environment="GROQ_API_KEY=your_key"
ExecStart=/opt/eon-brain/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable eon-brain
sudo systemctl start eon-brain
```

#### 3. Cloud Deployment (Google Cloud Run)

```bash
gcloud run deploy eon-brain \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GROQ_API_KEY=your_key
```

#### 4. Gunicorn with Nginx

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000 \
  --timeout 60 \
  --access-logfile /var/log/eon-brain/access.log \
  --error-logfile /var/log/eon-brain/error.log \
  app.main:app
```

Nginx configuration:
```nginx
upstream eon_brain {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://eon_brain;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
}
```

### Configuration

#### Environment Variables

```bash
# Required
GROQ_API_KEY=your_api_key

# Optional
LOG_LEVEL=INFO
DATABASE_PATH=/opt/data/sessions.db
SESSION_TIMEOUT=3600
CORS_ORIGINS=*
```

#### Performance Tuning

```python
# app/config.py additions
class Settings:
    # LLM
    LLM_TIMEOUT = 30
    MAX_RETRIES = 3
    
    # Memory
    MAX_CONVERSATION_HISTORY = 50
    SESSION_CLEANUP_DAYS = 7
    
    # Performance
    WORKER_THREADS = 4
    CONNECTION_POOL_SIZE = 10
```

### Monitoring

#### Health Checks

```bash
# Regular health checks
curl http://localhost:8000/health

# Application logs
tail -f /var/log/eon-brain/app.log

# Database status
sqlite3 sessions.db "SELECT COUNT(*) FROM sessions;"
```

#### Prometheus Metrics (Optional)

```python
from prometheus_client import Counter, Histogram

chat_requests = Counter('chat_requests_total', 'Total chat requests')
chat_duration = Histogram('chat_duration_seconds', 'Chat request duration')
```

### Backup & Recovery

#### Database Backup

```bash
# Regular backups
*/6 * * * * cp /opt/eon-brain/sessions.db /backup/sessions.db.$(date +\%s)

# Automated cleanup (keep 30 days)
find /backup -name "sessions.db.*" -mtime +30 -delete
```

#### Disaster Recovery

1. Stop the service: `systemctl stop eon-brain`
2. Restore backup: `cp backup/sessions.db sessions.db`
3. Verify: `sqlite3 sessions.db "SELECT COUNT(*) FROM sessions;"`
4. Restart: `systemctl start eon-brain`

### Security

#### SSL/TLS

```bash
# Let's Encrypt
sudo apt-get install certbot
certbot certonly --standalone -d your-domain.com

# Update Nginx config
ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
```

#### API Key Management

```bash
# Using AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id eon-brain-key

# Using HashiCorp Vault
vault read secret/eon-brain
```

#### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/chat")
@limiter.limit("100/minute")
async def chat(req: ChatRequest):
    ...
```

### Troubleshooting

#### Issue: High memory usage
**Solution**: 
- Reduce MAX_CONVERSATION_HISTORY
- Implement session cleanup more frequently
- Monitor with `top` or cloud monitoring

#### Issue: Slow responses
**Solution**:
- Check GROQ API status
- Increase worker count
- Enable response caching
- Check database performance

#### Issue: Database errors
**Solution**:
- Check disk space: `df -h`
- Repair database: `sqlite3 sessions.db "PRAGMA integrity_check;"`
- Clear old sessions manually

### Monitoring Dashboard

Set up monitoring with your preferred tool:

```yaml
# Prometheus scrape config
scrape_configs:
  - job_name: 'eon-brain'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Rollback Procedure

```bash
# Keep previous version
cp -r /opt/eon-brain /opt/eon-brain.backup.$(date +%Y%m%d)

# If issues occur, rollback:
systemctl stop eon-brain
rm -rf /opt/eon-brain
mv /opt/eon-brain.backup.YYYYMMDD /opt/eon-brain
systemctl start eon-brain
```

## Production Checklist

- [ ] GROQ API key secured
- [ ] SSL/TLS configured
- [ ] Rate limiting enabled
- [ ] Monitoring set up
- [ ] Logging configured
- [ ] Backup strategy implemented
- [ ] Database optimized
- [ ] CORS properly configured
- [ ] Error handling tested
- [ ] Performance tested under load
- [ ] Rollback plan ready
- [ ] Documentation updated
- [ ] Team trained on deployment
- [ ] Incident response plan ready

## Support

For deployment issues, check:
1. Application logs
2. System logs (journalctl -u eon-brain)
3. GROQ API status
4. Database integrity
5. Network connectivity
