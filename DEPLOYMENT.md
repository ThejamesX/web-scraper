# Deployment Guide for PriceScout

This guide provides comprehensive instructions for deploying PriceScout in various environments.

## Table of Contents
- [Quick Start with Docker](#quick-start-with-docker)
- [Production Deployment](#production-deployment)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Monitoring and Logging](#monitoring-and-logging)
- [Scaling Considerations](#scaling-considerations)

## Quick Start with Docker

The easiest way to deploy PriceScout is using Docker Compose:

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd web-scraper
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Build and start services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Web UI: http://localhost:8000
   - API Docs: http://localhost:8000/docs

5. **View logs**
   ```bash
   docker-compose logs -f web
   ```

6. **Stop services**
   ```bash
   docker-compose down
   ```

## Production Deployment

### 1. Using Docker Compose (Recommended for Small-Medium Scale)

**Production docker-compose configuration:**

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://pricescout:${DB_PASSWORD}@db:5432/pricescout
      - SCRAPER_HEADLESS=true
      - SCRAPER_MOCK_MODE=false
      - PRICE_CHECK_INTERVAL_HOURS=4
    depends_on:
      db:
        condition: service_healthy
    restart: always
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1'
          memory: 1G
    networks:
      - pricescout-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=pricescout
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=pricescout
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: always
    networks:
      - pricescout-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U pricescout"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - web
    restart: always
    networks:
      - pricescout-network

volumes:
  postgres_data:

networks:
  pricescout-network:
    driver: bridge
```

### 2. Kubernetes Deployment (For Large Scale)

**Deployment configuration (k8s-deployment.yaml):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pricescout-web
  labels:
    app: pricescout
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pricescout
  template:
    metadata:
      labels:
        app: pricescout
    spec:
      containers:
      - name: web
        image: pricescout:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: pricescout-secrets
              key: database-url
        - name: SCRAPER_HEADLESS
          value: "true"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

## Environment Configuration

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# API Configuration
API_TITLE=PriceScout API
API_VERSION=1.0.0
API_DESCRIPTION=E-commerce product search and price tracking API

# Scheduler
PRICE_CHECK_INTERVAL_HOURS=4

# Scraper
SCRAPER_TIMEOUT=30000
SCRAPER_HEADLESS=true
SCRAPER_MOCK_MODE=false
```

### Optional Environment Variables

```bash
# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
API_KEY_ENABLED=false

# Performance
MAX_CONCURRENT_SCRAPES=5
CONNECTION_POOL_SIZE=20
```

## Database Setup

### PostgreSQL Production Setup

1. **Create database and user**
   ```sql
   CREATE DATABASE pricescout;
   CREATE USER pricescout WITH ENCRYPTED PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE pricescout TO pricescout;
   ```

2. **Configure connection pooling**
   - Use pgBouncer for connection pooling in high-traffic scenarios
   - Configure in DATABASE_URL: `postgresql+asyncpg://user:pass@pgbouncer:6432/dbname`

3. **Backup strategy**
   ```bash
   # Automated daily backups
   0 2 * * * pg_dump -U pricescout pricescout > /backups/pricescout_$(date +\%Y\%m\%d).sql
   
   # Keep last 7 days
   find /backups -name "pricescout_*.sql" -mtime +7 -delete
   ```

### Database Migration

Currently using SQLAlchemy's create_all() for development. For production:

1. **Install Alembic**
   ```bash
   pip install alembic
   ```

2. **Initialize Alembic**
   ```bash
   alembic init alembic
   ```

3. **Create migration**
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   ```

4. **Apply migration**
   ```bash
   alembic upgrade head
   ```

## Monitoring and Logging

### Application Logging

Configure structured logging in production:

```python
# Add to main.py
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'json',
            'filename': '/var/log/pricescout/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### Health Checks

The `/health` endpoint provides application health status:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "scheduler_running": true,
  "price_check_interval_hours": 4
}
```

### Metrics and Monitoring

Recommended tools:
- **Prometheus**: For metrics collection
- **Grafana**: For visualization
- **Sentry**: For error tracking
- **ELK Stack**: For log aggregation

## Scaling Considerations

### Horizontal Scaling

1. **Stateless Design**: The application is stateless and can scale horizontally
2. **Load Balancer**: Use Nginx or cloud load balancer
3. **Session Management**: Currently no sessions, future: use Redis for session store

### Database Scaling

1. **Read Replicas**: Set up PostgreSQL read replicas for read-heavy workloads
2. **Connection Pooling**: Use pgBouncer to manage connections efficiently
3. **Indexes**: Already configured on frequently queried columns

### Scraping Optimization

1. **Distributed Scraping**: Consider using Celery for distributed task queue
2. **Rate Limiting**: Implement per-site rate limiting to avoid blocks
3. **Proxy Rotation**: Use proxy services for high-volume scraping

### Caching Strategy

Future enhancement: Add Redis for caching
- Cache search results (TTL: 1 hour)
- Cache product details (TTL: 30 minutes)
- Cache price history (TTL: 5 minutes)

## SSL/TLS Configuration

### Using Let's Encrypt with Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security Best Practices

1. **Environment Variables**: Never commit secrets to version control
2. **Database**: Use strong passwords and encrypted connections
3. **API**: Implement rate limiting (future enhancement)
4. **CORS**: Configure allowed origins in production
5. **Dependencies**: Regularly update dependencies for security patches
6. **HTTPS**: Always use HTTPS in production
7. **Non-root User**: Docker container runs as non-root user

## Backup and Disaster Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh - Database backup script

BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="pricescout"

# Create backup
docker-compose exec -T db pg_dump -U pricescout $DB_NAME | gzip > "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

# Keep last 7 days
find $BACKUP_DIR -name "${DB_NAME}_*.sql.gz" -mtime +7 -delete

# Upload to S3 (optional)
# aws s3 cp "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz" s3://your-bucket/backups/
```

### Restore from Backup

```bash
# Extract backup
gunzip pricescout_20240115_120000.sql.gz

# Restore to database
docker-compose exec -T db psql -U pricescout pricescout < pricescout_20240115_120000.sql
```

## Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   # Check logs
   docker-compose logs web
   
   # Check container status
   docker-compose ps
   ```

2. **Database connection errors**
   - Verify DATABASE_URL is correct
   - Ensure database is accessible
   - Check database logs: `docker-compose logs db`

3. **Scraping failures**
   - Ensure Playwright browsers are installed
   - Check SCRAPER_HEADLESS setting
   - Verify internet connectivity
   - Enable SCRAPER_MOCK_MODE for testing

4. **High memory usage**
   - Limit Playwright browser instances
   - Configure memory limits in docker-compose
   - Monitor with: `docker stats`

## Performance Tuning

### Uvicorn Workers

For production, use multiple workers:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Database Connection Pool

Configure in DATABASE_URL:
```
postgresql+asyncpg://user:pass@host/db?pool_size=20&max_overflow=10
```

## Conclusion

This deployment guide covers the essential aspects of deploying PriceScout. For specific cloud providers (AWS, GCP, Azure), additional configuration may be required. Always test deployments in a staging environment before production.

For questions or issues, please refer to the main README.md or open an issue on GitHub.
