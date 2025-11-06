# 🚀 Cite-Agent Deployment Guide
## Plug-and-Play Production Deployment

**Time to deploy:** 10 minutes
**Difficulty:** Easy
**Requirements:** Docker, Docker Compose

---

## Quick Start (TL;DR)

```bash
# 1. Clone and configure
git clone <your-repo>
cd cite-agent
cp .env.example .env
# Edit .env with your API keys

# 2. Start everything
docker-compose up -d

# 3. Access services
# API: http://localhost:8000
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

**That's it!** Your production-ready Cite-Agent is running with full monitoring.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Configuration](#configuration)
3. [Deployment](#deployment)
4. [Verification](#verification)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)
7. [Production Hardening](#production-hardening)
8. [Scaling](#scaling)

---

## Prerequisites

### Required

- **Docker** 20.10+ ([Install](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.0+ ([Install](https://docs.docker.com/compose/install/))
- **4GB RAM** minimum (8GB+ recommended)
- **10GB disk space** minimum

### API Keys Needed

You'll need at least ONE of these LLM provider API keys:

- **Groq** (Primary, recommended): https://console.groq.com/keys
- **Cerebras** (Fast inference): https://inference.cerebras.ai
- **OpenAI** (Fallback): https://platform.openai.com/api-keys

Optional but recommended:
- **FinSight API** for financial data: https://financialmodelingprep.com

---

## Configuration

### Step 1: Create Environment File

```bash
cp .env.example .env
```

### Step 2: Edit Configuration

Open `.env` and fill in **minimum required values**:

```bash
# REQUIRED: Database password
POSTGRES_PASSWORD=your_strong_password_here

# REQUIRED: At least one LLM API key
GROQ_API_KEY=gsk_your_key_here

# REQUIRED: JWT secret (for production)
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(64))"
JWT_SECRET=your_generated_secret_here

# OPTIONAL but recommended
CEREBRAS_API_KEY=your_cerebras_key_here
FINSIGHT_API_KEY=your_finsight_key_here
```

### Step 3: Review Settings

**For development:**
```bash
ENVIRONMENT=development
DEBUG=1
LOG_LEVEL=DEBUG
```

**For production:**
```bash
ENVIRONMENT=production
DEBUG=0
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://yourdomain.com
```

---

## Deployment

### Option 1: Full Stack (Recommended)

Deploys API + Database + Redis + Prometheus + Grafana

```bash
docker-compose up -d
```

**Services started:**
- `cite-agent-postgres` - PostgreSQL database
- `cite-agent-redis` - Redis cache
- `cite-agent-api` - Main API server
- `cite-agent-prometheus` - Metrics collection
- `cite-agent-grafana` - Metrics visualization

### Option 2: Minimal Stack

Just API + Database + Redis (no monitoring)

```bash
docker-compose up -d postgres redis api
```

### Option 3: With Alerting

Includes AlertManager for notifications

```bash
docker-compose --profile monitoring-full up -d
```

---

## Verification

### Step 1: Check Services Health

```bash
# Check all containers are running
docker-compose ps

# Expected output:
# NAME                     STATUS
# cite-agent-postgres      Up (healthy)
# cite-agent-redis         Up (healthy)
# cite-agent-api           Up (healthy)
# cite-agent-prometheus    Up
# cite-agent-grafana       Up
```

### Step 2: Test API Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.4.1",
  "services": {
    "database": "up",
    "redis": "up",
    "llm_providers": ["groq", "cerebras"]
  }
}
```

### Step 3: Test API Request

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is AI?",
    "model": "openai/gpt-oss-120b"
  }'
```

### Step 4: Check Logs

```bash
# View API logs
docker-compose logs -f api

# View all logs
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100 api
```

---

## Monitoring

### Access Grafana Dashboard

1. Open http://localhost:3000
2. Login: `admin` / `admin` (change on first login)
3. Go to **Dashboards** → **Cite-Agent Overview**

**You should see:**
- Request rate (requests/sec)
- Success rate (%)
- P95 latency (seconds)
- Memory usage (MB)
- Error rates
- Latency percentiles graph

### Access Prometheus

1. Open http://localhost:9090
2. Try queries:
   ```promql
   # Request rate
   rate(http_requests_total[5m])

   # Success rate
   sum(rate(http_requests_total{status=~"2.."}[5m])) / sum(rate(http_requests_total[5m]))

   # P95 latency
   histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
   ```

### View Metrics Endpoint

```bash
curl http://localhost:8000/metrics
```

---

## Troubleshooting

### API Won't Start

**Check logs:**
```bash
docker-compose logs api
```

**Common issues:**

1. **Database connection failed**
   ```bash
   # Check postgres is up
   docker-compose ps postgres

   # Check database logs
   docker-compose logs postgres

   # Restart postgres
   docker-compose restart postgres
   ```

2. **Missing API keys**
   ```
   Error: GROQ_API_KEY not set
   ```
   → Edit `.env` and add your API key

3. **Port already in use**
   ```
   Error: port 8000 already allocated
   ```
   → Change port in docker-compose.yml or stop conflicting service

### Database Issues

**Reset database:**
```bash
docker-compose down -v  # WARNING: Deletes all data
docker-compose up -d
```

**Access database:**
```bash
docker-compose exec postgres psql -U cite_agent
```

### Redis Issues

**Check Redis:**
```bash
docker-compose exec redis redis-cli ping
# Should return: PONG
```

**Clear Redis cache:**
```bash
docker-compose exec redis redis-cli FLUSHALL
```

### High Memory Usage

**Check memory:**
```bash
docker stats cite-agent-api
```

**If >2GB:**
- Check for memory leaks in logs
- Verify session archival is working
- Restart API: `docker-compose restart api`

### Grafana Dashboard Not Showing Data

1. **Check Prometheus is scraping:**
   - Go to http://localhost:9090/targets
   - All targets should be "UP"

2. **Check datasource:**
   - Grafana → Configuration → Data sources
   - Prometheus should be green

3. **Reload dashboard:**
   - Go to dashboard
   - Click refresh icon (top right)
   - Change time range to "Last 5 minutes"

---

## Production Hardening

### 1. Secure Secrets

**Never commit `.env` file!**

```bash
# Already in .gitignore, but double-check:
git status .env
# Should not appear
```

**Use strong passwords:**
```bash
# Generate secure password
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Enable HTTPS

**Option A: Use reverse proxy (nginx)**

```nginx
server {
    listen 443 ssl;
    server_name api.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Option B: Use Caddy (automatic HTTPS)**

```bash
# Caddyfile
api.yourdomain.com {
    reverse_proxy localhost:8000
}
```

### 3. Set Resource Limits

Edit `docker-compose.yml`:

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 512M
```

### 4. Configure Backups

**Database backup script:**

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U cite_agent cite_agent > backup_$DATE.sql
gzip backup_$DATE.sql
```

**Automated backups (cron):**
```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup.sh
```

### 5. Enable Alerts

Edit `monitoring/alertmanager.yml`:

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@yourdomain.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'your-app-password'

route:
  receiver: 'email'
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

receivers:
  - name: 'email'
    email_configs:
      - to: 'ops@yourdomain.com'
        send_resolved: true
```

Then restart:
```bash
docker-compose restart alertmanager
```

---

## Scaling

### Horizontal Scaling

**Run multiple API instances:**

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      replicas: 3  # Run 3 instances
```

**Add load balancer:**

```yaml
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
    depends_on:
      - api
```

### Vertical Scaling

**Increase resources:**

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
```

### Database Scaling

**Enable connection pooling:**

```yaml
  api:
    environment:
      DATABASE_URL: postgresql://cite_agent:password@postgres:5432/cite_agent?pool_size=20&max_overflow=10
```

**Use read replicas** (for high traffic):
- Configure PostgreSQL streaming replication
- Route read queries to replicas

---

## Kubernetes Deployment

**Coming soon:** Full Kubernetes manifests

For now, use Kompose to convert:

```bash
kompose convert -f docker-compose.yml
kubectl apply -f .
```

---

## Maintenance

### Update to Latest Version

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

### View System Status

```bash
# Resource usage
docker stats

# Disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

### Rotate Logs

```bash
# Configure log rotation in docker-compose.yml
services:
  api:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## Getting Help

### Check Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Production Hardening](docs/PRODUCTION_HARDENING_PHASE3.md)
- [Testing Guide](TESTING.md)

### Common Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a service
docker-compose restart api

# View logs
docker-compose logs -f api

# Execute command in container
docker-compose exec api sh

# Check resource usage
docker stats

# Rebuild after code changes
docker-compose build api
docker-compose up -d api
```

---

## Production Checklist

Before going live, verify:

- [ ] All API keys configured in `.env`
- [ ] Strong passwords for all services
- [ ] JWT_SECRET is long and random
- [ ] HTTPS enabled (reverse proxy configured)
- [ ] CORS origins restricted to your domains
- [ ] Grafana dashboard accessible and showing data
- [ ] Prometheus alerts configured
- [ ] Database backups automated
- [ ] Resource limits set appropriately
- [ ] Logs rotating properly
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Error tracking configured (Sentry)
- [ ] Monitoring alerts delivered to ops team

---

## Success! 🎉

Your Cite-Agent is now running in production with:

✅ Full monitoring (Prometheus + Grafana)
✅ Automatic health checks
✅ Production-grade database
✅ Redis caching
✅ Comprehensive alerting
✅ Easy scaling

**Next steps:**
1. Configure your domain/DNS
2. Set up HTTPS
3. Run load tests
4. Monitor dashboards
5. Tune performance

**Need help?** Check the docs or create an issue on GitHub.
