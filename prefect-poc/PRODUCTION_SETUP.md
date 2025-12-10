# Prefect Production Setup Guide

How to prepare Prefect for production deployment, including disabling telemetry.

---

## 🔕 Disabling Telemetry (Recommended for Production)

The telemetry error you see is **harmless** - it's just Prefect trying to send anonymous usage stats. Your pipeline runs perfectly regardless!

### Option 1: Disable via Environment Variable

```bash
export PREFECT_DISABLE_TELEMETRY=true
python run_modular.py
```

**Or permanently in your shell profile:**

```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export PREFECT_DISABLE_TELEMETRY=true' >> ~/.zshrc
source ~/.zshrc
```

### Option 2: Disable via Prefect Config

```bash
prefect config set PREFECT_DISABLE_TELEMETRY=true
```

### Option 3: Disable in Code

```python
# At the top of run_modular.py
import os
os.environ['PREFECT_DISABLE_TELEMETRY'] = 'true'

# Then your normal code...
```

### Option 4: Disable in Docker

```dockerfile
FROM python:3.9
ENV PREFECT_DISABLE_TELEMETRY=true
# ... rest of Dockerfile
```

---

## 🚀 Production Deployment Options

### 1. **Local Server (Self-Hosted)**

**Pros:**
- Full control
- No costs
- Data stays internal

**Setup:**
```bash
# Install Prefect
pip install prefect

# Disable telemetry
export PREFECT_DISABLE_TELEMETRY=true

# Start server
prefect server start --host 0.0.0.0 --port 4200

# Start worker
prefect worker start --pool default
```

**Run as service (systemd):**

```ini
# /etc/systemd/system/prefect-server.service
[Unit]
Description=Prefect Server
After=network.target

[Service]
Type=simple
User=prefect
Environment="PREFECT_DISABLE_TELEMETRY=true"
ExecStart=/usr/local/bin/prefect server start
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable prefect-server
sudo systemctl start prefect-server
```

---

### 2. **Docker Deployment**

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  prefect-server:
    image: prefecthq/prefect:2-python3.9
    environment:
      - PREFECT_DISABLE_TELEMETRY=true
      - PREFECT_SERVER_API_HOST=0.0.0.0
      - PREFECT_SERVER_API_PORT=4200
    ports:
      - "4200:4200"
    volumes:
      - prefect_data:/root/.prefect
    command: prefect server start --host 0.0.0.0

  prefect-worker:
    image: prefecthq/prefect:2-python3.9
    environment:
      - PREFECT_DISABLE_TELEMETRY=true
      - PREFECT_API_URL=http://prefect-server:4200/api
    depends_on:
      - prefect-server
    volumes:
      - ./prefect_poc:/app/prefect_poc
      - ./run_modular.py:/app/run_modular.py
    working_dir: /app
    command: prefect worker start --pool default

volumes:
  prefect_data:
```

**Run:**
```bash
docker-compose up -d
```

---

### 3. **Kubernetes Deployment**

**prefect-deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prefect-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prefect-server
  template:
    metadata:
      labels:
        app: prefect-server
    spec:
      containers:
      - name: prefect
        image: prefecthq/prefect:2-python3.9
        env:
        - name: PREFECT_DISABLE_TELEMETRY
          value: "true"
        - name: PREFECT_SERVER_API_HOST
          value: "0.0.0.0"
        ports:
        - containerPort: 4200
        command: ["prefect", "server", "start", "--host", "0.0.0.0"]
---
apiVersion: v1
kind: Service
metadata:
  name: prefect-server
spec:
  selector:
    app: prefect-server
  ports:
  - port: 4200
    targetPort: 4200
```

**Deploy:**
```bash
kubectl apply -f prefect-deployment.yaml
```

---

### 4. **Prefect Cloud (Easiest)**

**Pros:**
- No server management
- Managed workers
- Built-in monitoring
- Free tier available

**Setup:**
```bash
# Login to Prefect Cloud
prefect cloud login

# Deploy flow
python prefect_poc/schedule_example.py

# Cloud handles workers automatically!
```

**No telemetry errors** - cloud handles everything!

---

## 🔒 Production Best Practices

### 1. **Use Environment Variables for Secrets**

```python
import os
from prefect.blocks.system import Secret

# Don't hardcode!
API_KEY = os.getenv('API_KEY')

# Or use Prefect Secrets
api_key = Secret.load("api-key")
```

### 2. **Configure Retries**

```python
@task(retries=3, retry_delay_seconds=60)
def fetch_data():
    # Auto-retry on failure
    pass
```

### 3. **Set Timeouts**

```python
@task(timeout_seconds=300)  # 5 minutes max
def long_running_task():
    pass
```

### 4. **Use Work Pools**

```bash
# Create work pool
prefect work-pool create production-pool

# Start worker
prefect worker start --pool production-pool
```

### 5. **Monitor with Prefect UI**

```bash
# Access UI at http://your-server:4200
# Monitor runs, logs, schedules
```

---

## 📊 Comparison: Self-Hosted vs Cloud

| Feature | Self-Hosted | Prefect Cloud |
|---------|-------------|---------------|
| **Cost** | Free | Free tier / Paid |
| **Setup** | Manual | Automatic |
| **Maintenance** | You manage | Managed |
| **Telemetry** | Can disable | Not an issue |
| **Control** | Full control | Less control |
| **Scaling** | Manual | Automatic |
| **Best For** | Internal/enterprise | Quick start/SaaS |

---

## 🐳 Quick Production Docker Setup

**Dockerfile:**

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Disable telemetry
ENV PREFECT_DISABLE_TELEMETRY=true

# Install dependencies
COPY prefect-poc/setup.py .
RUN pip install -e .

# Copy application
COPY prefect-poc/prefect_poc ./prefect_poc
COPY prefect-poc/run_modular.py .

# Run
CMD ["python", "run_modular.py"]
```

**Build and run:**
```bash
docker build -t prefect-pipeline .
docker run prefect-pipeline
```

---

## ⚙️ Environment Variables for Production

```bash
# Telemetry
export PREFECT_DISABLE_TELEMETRY=true

# Server URL
export PREFECT_API_URL=http://your-prefect-server:4200/api

# Logging
export PREFECT_LOGGING_LEVEL=INFO

# Database (for persistent storage)
export PREFECT_API_DATABASE_CONNECTION_URL=postgresql://user:pass@localhost/prefect

# Workers
export PREFECT_WORKER_PREFETCH_SECONDS=10
```

---

## 🔍 Troubleshooting Production Issues

### Issue: Telemetry Error

**Solution:**
```bash
export PREFECT_DISABLE_TELEMETRY=true
```

### Issue: Worker Not Picking Up Flows

**Check:**
```bash
prefect worker ls  # List workers
prefect work-pool ls  # List work pools
```

### Issue: Database Connection

**Use PostgreSQL in production:**
```bash
export PREFECT_API_DATABASE_CONNECTION_URL=postgresql://user:pass@host/db
prefect server database upgrade
```

### Issue: Performance

**Scale workers:**
```bash
# Start multiple workers
for i in {1..5}; do
  prefect worker start --pool default --name worker-$i &
done
```

---

## 📚 Production Checklist

- [ ] Disable telemetry
- [ ] Use PostgreSQL (not SQLite)
- [ ] Set up proper logging
- [ ] Configure retries and timeouts
- [ ] Use environment variables for secrets
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Use work pools for organization
- [ ] Implement error notifications
- [ ] Document deployment process

---

## 🎯 Recommendation

**For Your Use Case:**

### If Budget = $0:
✅ **Self-hosted with Docker** + telemetry disabled

### If Want Easiest:
✅ **Prefect Cloud free tier**

### If Enterprise:
✅ **Self-hosted Kubernetes** + PostgreSQL + monitoring

---

## 🚀 Quick Start (Production)

```bash
# 1. Disable telemetry
export PREFECT_DISABLE_TELEMETRY=true

# 2. Start server
prefect server start &

# 3. Create deployment
python prefect_poc/schedule_example.py

# 4. Start worker
prefect worker start --pool default

# Done! No more telemetry errors!
```

---

**Bottom line:** The telemetry error is **cosmetic only**. Just disable it in production! 🎉
