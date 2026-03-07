# 🚀 Deployment Guide

Complete guide for deploying Genesis Collective Consciousness Network to production.

## Overview

This guide covers deploying Genesis from development to production environments, including cloud platforms, security hardening, and operational best practices.

## Pre-Deployment Checklist

### Code Readiness
- [ ] All tests passing
- [ ] No critical bugs
- [ ] Security audit completed
- [ ] Performance tested
- [ ] Documentation updated

### Infrastructure
- [ ] Hosting platform selected
- [ ] Domain name registered
- [ ] SSL certificate obtained
- [ ] Database provisioned
- [ ] Backup strategy defined

### Configuration
- [ ] Environment variables documented
- [ ] Secrets management configured
- [ ] Logging set up
- [ ] Monitoring tools ready
- [ ] Error tracking configured

## Production Environment Setup

### System Requirements

**Minimum** (supports ~100 concurrent users):
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **Network**: 10Mbps

**Recommended** (supports ~1000 concurrent users):
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 100GB SSD
- **Network**: 100Mbps

**High-Scale** (supports 10,000+ concurrent users):
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Storage**: 500GB+ SSD
- **Network**: 1Gbps
- **Load Balancer**: Required
- **Database**: Dedicated server

### Operating System

Recommended: **Ubuntu 22.04 LTS** or **Debian 11**

Also supported:
- CentOS/RHEL 8+
- Amazon Linux 2
- Windows Server 2019+

## Database Setup

### PostgreSQL (Recommended)

**Installation**:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Configuration**:
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE genesis_prod;
CREATE USER genesis_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE genesis_prod TO genesis_user;
\q
```

**Connection String**:
```bash
export DATABASE_URL="postgresql://genesis_user:secure_password_here@localhost/genesis_prod"
```

**Performance Tuning**:
```sql
-- In postgresql.conf
shared_buffers = 2GB              # 25% of RAM
effective_cache_size = 6GB        # 75% of RAM
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1            # For SSD
work_mem = 10MB
```

### Database Migrations

Create migration script:
```bash
# scripts/migrate_to_postgres.py
import sqlite3
import psycopg2

# Export from SQLite
sqlite_conn = sqlite3.connect('collective_memory.db')
# Import to PostgreSQL
pg_conn = psycopg2.connect(DATABASE_URL)
# Migration logic here
```

## Application Server Setup

### Using Gunicorn (Recommended)

**Installation**:
```bash
pip install gunicorn gevent
```

**Configuration** (`gunicorn_config.py`):
```python
# gunicorn_config.py
bind = "0.0.0.0:5003"
workers = 4  # 2 * CPU_CORES + 1
worker_class = "gevent"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "/var/log/genesis/access.log"
errorlog = "/var/log/genesis/error.log"
loglevel = "info"

# Security
limit_request_line = 4096
limit_request_fields = 100
```

**Running**:
```bash
gunicorn -c gunicorn_config.py Genesis.wsgi:app
```

**Systemd Service** (`/etc/systemd/system/genesis.service`):
```ini
[Unit]
Description=Genesis Collective Consciousness
After=network.target postgresql.service

[Service]
Type=notify
User=genesis
Group=genesis
WorkingDirectory=/opt/genesis
Environment="PATH=/opt/genesis/.venv/bin"
Environment="DATABASE_URL=postgresql://..."
ExecStart=/opt/genesis/.venv/bin/gunicorn -c gunicorn_config.py Genesis.wsgi:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and Start**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable genesis
sudo systemctl start genesis
sudo systemctl status genesis
```

### Using uWSGI (Alternative)

**Installation**:
```bash
pip install uwsgi
```

**Configuration** (`uwsgi.ini`):
```ini
[uwsgi]
module = Genesis.wsgi:app
master = true
processes = 4
threads = 2
socket = /tmp/genesis.sock
chmod-socket = 660
vacuum = true
die-on-term = true
```

## Reverse Proxy Setup

### Nginx (Recommended)

**Installation**:
```bash
sudo apt install nginx
```

**Configuration** (`/etc/nginx/sites-available/genesis`):
```nginx
upstream genesis_app {
    server 127.0.0.1:5003 fail_timeout=0;
}

server {
    listen 80;
    server_name genesis.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name genesis.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/genesis.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/genesis.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Logging
    access_log /var/log/nginx/genesis-access.log;
    error_log /var/log/nginx/genesis-error.log;
    
    # Client body size limit
    client_max_body_size 10M;
    
    # Static files
    location /static {
        alias /opt/genesis/Genesis/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # API and app
    location / {
        proxy_pass http://genesis_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
    
    # WebSocket support (if needed)
    location /ws {
        proxy_pass http://genesis_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Enable Site**:
```bash
sudo ln -s /etc/nginx/sites-available/genesis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL Certificate with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d genesis.yourdomain.com

# Auto-renewal (already set up by certbot)
sudo certbot renew --dry-run
```

## Security Hardening

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
```

### Application Security

**Environment Variables** (`.env`):
```bash
# Never commit this file!
SECRET_KEY=generate_long_random_string_here
DATABASE_URL=postgresql://user:password@localhost/genesis_prod
FLASK_ENV=production
DEBUG=False

# API Keys
OPENAI_API_KEY=your_key_here

# Security
ALLOWED_HOSTS=genesis.yourdomain.com
CORS_ORIGINS=https://genesis.yourdomain.com
```

**Generate Secret Key**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Security Headers** (in Flask app):
```python
from flask_talisman import Talisman

Talisman(app, 
    force_https=True,
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'"
    }
)
```

### User Authentication

For production, implement proper authentication:

```python
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

# Hash passwords
hashed = generate_password_hash('user_password', method='pbkdf2:sha256')

# Verify passwords
check_password_hash(hashed, 'user_password')
```

## Monitoring & Logging

### Application Logging

**Configure logging** (`logging_config.py`):
```python
import logging
from logging.handlers import RotatingFileHandler

# Create logger
logger = logging.getLogger('genesis')
logger.setLevel(logging.INFO)

# File handler
handler = RotatingFileHandler(
    '/var/log/genesis/app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)

# Format
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)
handler.setFormatter(formatter)

logger.addHandler(handler)
```

### System Monitoring

**Install monitoring tools**:
```bash
# Prometheus + Grafana
sudo apt install prometheus grafana

# Or use cloud monitoring
# - AWS CloudWatch
# - Azure Monitor
# - Google Cloud Monitoring
```

**Monitor metrics**:
- CPU/Memory usage
- Request rates
- Response times
- Error rates
- Database performance

### Error Tracking

**Sentry Integration**:
```bash
pip install sentry-sdk[flask]
```

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your_sentry_dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

## Backup Strategy

### Database Backups

**Automated PostgreSQL backup**:
```bash
#!/bin/bash
# /opt/genesis/scripts/backup_db.sh

BACKUP_DIR="/backup/genesis"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump genesis_prod > "$BACKUP_DIR/genesis_$DATE.sql"

# Compress
gzip "$BACKUP_DIR/genesis_$DATE.sql"

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

**Cron job**:
```bash
# Run daily at 2 AM
0 2 * * * /opt/genesis/scripts/backup_db.sh
```

### File Backups

```bash
# Backup code and configuration
tar -czf genesis_files_$(date +%Y%m%d).tar.gz \
    /opt/genesis \
    --exclude='*.pyc' \
    --exclude='.venv' \
    --exclude='__pycache__'
```

## Cloud Platform Deployment

### AWS Deployment

**Using Elastic Beanstalk**:
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 genesis-app

# Create environment
eb create genesis-prod

# Deploy
eb deploy

# Open in browser
eb open
```

**Configuration** (`.ebextensions/genesis.config`):
```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    FLASK_ENV: production
    DATABASE_URL: postgresql://...
  aws:elasticbeanstalk:container:python:
    WSGIPath: Genesis.wsgi:app
```

### Azure Deployment

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login
az login

# Create resource group
az group create --name genesis-rg --location eastus

# Create App Service plan
az appservice plan create --name genesis-plan --resource-group genesis-rg --sku B1 --is-linux

# Create web app
az webapp create --resource-group genesis-rg --plan genesis-plan --name genesis-app --runtime "PYTHON:3.11"

# Deploy
az webapp deployment source config-local-git --name genesis-app --resource-group genesis-rg
git remote add azure <git-url>
git push azure main
```

### Google Cloud Platform

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# Initialize
gcloud init

# Create app.yaml
echo "runtime: python311" > app.yaml

# Deploy
gcloud app deploy
```

### Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY Genesis/ ./Genesis/
COPY *.py ./

# Create non-root user
RUN useradd -m genesis && chown -R genesis:genesis /app
USER genesis

# Expose port
EXPOSE 5003

# Run with gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "Genesis.wsgi:app"]
```

**Docker Compose** (`docker-compose.yml`):
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5003:5003"
    environment:
      - DATABASE_URL=postgresql://genesis:password@db:5432/genesis
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
    restart: always

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=genesis
      - POSTGRES_USER=genesis
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - app
    restart: always

volumes:
  postgres_data:
```

**Deploy**:
```bash
docker-compose up -d
```

## Performance Optimization

### Caching

**Redis Setup**:
```bash
sudo apt install redis-server
pip install redis flask-caching
```

**Configuration**:
```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
})

@cache.memoize(timeout=300)
def get_collective_insights():
    # Expensive operation
    return insights
```

### Database Optimization

```sql
-- Add indexes
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_created ON conversations(created_at);
CREATE INDEX idx_patterns_type ON patterns(pattern_type);

-- Analyze tables
ANALYZE conversations;
ANALYZE patterns;
```

### Load Balancing

**Nginx load balancing**:
```nginx
upstream genesis_cluster {
    least_conn;
    server 10.0.1.10:5003;
    server 10.0.1.11:5003;
    server 10.0.1.12:5003;
}
```

## Maintenance

### Regular Tasks

**Daily**:
- Check error logs
- Monitor resource usage
- Verify backups completed

**Weekly**:
- Review security alerts
- Check for updates
- Analyze performance metrics

**Monthly**:
- Update dependencies
- Security audit
- Capacity planning review

### Updates

```bash
# Backup first!
./scripts/backup_all.sh

# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run migrations
python scripts/migrate.py

# Restart services
sudo systemctl restart genesis
sudo systemctl restart nginx
```

## Troubleshooting Production

See [Troubleshooting Guide](Troubleshooting.md) for detailed solutions.

**Quick checks**:
```bash
# Service status
sudo systemctl status genesis

# Recent logs
sudo journalctl -u genesis -n 100

# Database connectivity
psql $DATABASE_URL -c "SELECT 1"

# Disk space
df -h

# Memory usage
free -m
```

## Support

For deployment assistance:
- **Email**: deploy@synthsara.org
- **GitHub Issues**: Technical problems
- **Discord**: Community help

---

**"Deployment is not the end—it's the beginning of serving at scale. Deploy with intention, monitor with care, improve with wisdom."**

🚀 Genesis deployed is Genesis serving the world. Handle this sacred responsibility with care.
