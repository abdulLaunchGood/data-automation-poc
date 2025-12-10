# Prefect Modular POC

Production-ready Prefect implementation with modular organization (similar to Dagster's asset structure).

## 📁 Project Structure

```
prefect-poc/
├── prefect_poc/
│   ├── tasks/                    # Modular tasks organized by domain
│   │   ├── sources/             # Data extraction
│   │   │   ├── __init__.py
│   │   │   └── api.py           # API fetching tasks
│   │   ├── transforms/          # Data transformation
│   │   │   ├── __init__.py
│   │   │   └── cleaning.py      # Cleaning & enrichment tasks
│   │   ├── analytics/           # Analytics & statistics
│   │   │   ├── __init__.py
│   │   │   └── stats.py         # Analytics tasks
│   │   └── exports/             # Data exports
│   │       ├── __init__.py
│   │       └── files.py         # File export tasks
│   ├── modular_flow.py          # Main orchestration flow
│   ├── schedule_example.py      # Scheduling examples
│   ├── flows.py                 # Simple flow (legacy)
│   └── tasks.py                 # Simple tasks (legacy)
└── tests/
    ├── test_modular_tasks.py    # Unit tests for modular tasks
    └── test_tasks.py            # Unit tests for simple tasks
```

## 🚀 Quick Start

### Run Without Server (Recommended for Testing)

```bash
cd prefect-poc
python prefect_poc/modular_flow.py
```

Output files created in `output/` directory:
- `prefect_modular_users.csv`
- `prefect_modular_posts_enriched.csv`
- `prefect_modular_user_stats.csv`
- `prefect_modular_top_authors.csv`
- `prefect_modular_summary.csv`

### Run With Scheduling

**Step 1: Start Prefect Server**
```bash
prefect server start
```

**Step 2: Create Deployments**
```bash
python prefect_poc/schedule_example.py
```

This creates 4 scheduled deployments:
- `daily-data-refresh` - Daily at 2 AM
- `six-hourly-refresh` - Every 6 hours
- `hourly-refresh` - Every hour
- `business-hours-refresh` - 9 AM-5 PM, Mon-Fri

**Step 3: Start Worker**
```bash
prefect worker start --pool default
```

## 📊 Pipeline Stages

### 1. **Sources** (Data Extraction)
```python
from prefect_poc.tasks.sources import fetch_users_task, fetch_posts_task

users = fetch_users_task()
posts = fetch_posts_task()
```

### 2. **Transforms** (Data Cleaning)
```python
from prefect_poc.tasks.transforms import clean_users_task, clean_posts_task, enrich_posts_task

users_clean = clean_users_task(users)
posts_clean = clean_posts_task(posts)
posts_enriched = enrich_posts_task(posts_clean, users_clean)
```

### 3. **Analytics** (Statistics)
```python
from prefect_poc.tasks.analytics import user_activity_task, top_authors_task, summary_task

user_stats = user_activity_task(posts_clean, users_clean)
top_authors = top_authors_task(user_stats)
summary = summary_task(users_clean, posts_clean, posts_enriched)
```

### 4. **Exports** (Save to Files)
```python
from prefect_poc.tasks.exports import export_users_task, export_posts_task

export_users_task(users_clean)
export_posts_task(posts_enriched)
```

## 🧪 Running Tests

```bash
# Run all tests
cd prefect-poc
pytest tests/test_modular_tasks.py -v

# Run specific test class
pytest tests/test_modular_tasks.py::TestSourceTasks -v

# Run specific test
pytest tests/test_modular_tasks.py::TestSourceTasks::test_fetch_users_task -v
```

## 🔧 Key Features

### ✅ Modular Organization
- Tasks grouped by domain (sources, transforms, analytics, exports)
- Similar structure to Dagster's assets
- Easy to understand and maintain

### ✅ No Server Required
- Run directly: `python prefect_poc/modular_flow.py`
- Server only needed for UI and scheduling

### ✅ Comprehensive Testing
- Unit tests for all tasks
- Mock external dependencies
- Test isolation with temp directories

### ✅ Production-Ready Features
- Retry logic on API tasks
- Proper logging
- Error handling
- Task tagging for organization

### ✅ Flexible Scheduling
- Cron schedules
- Interval schedules
- Multiple deployment options

## 📝 Task Features

### Retries
```python
@task(name="fetch_users", retries=3, retry_delay_seconds=5)
def fetch_users_task():
    # Auto-retries on failure
```

### Tags
```python
@task(name="clean_users", tags=["transform", "cleaning"])
def clean_users_task(users_raw):
    # Tagged for easy filtering
```

### Logging
```python
from prefect.logging import get_run_logger

@task
def my_task():
    logger = get_run_logger()
    logger.info("Processing data...")
```

## 🆚 Comparison: Simple vs Modular

### Simple Flow (flows.py)
- Single file
- Good for learning
- Quick prototyping

### Modular Flow (modular_flow.py)
- Organized by domain
- Production-ready
- Easy to scale
- Better for teams

## 💡 Adding New Tasks

### 1. Add Source Task
```python
# prefect_poc/tasks/sources/api.py
@task(name="fetch_new_data", tags=["api", "sources"])
def fetch_new_data_task():
    return {"data": fetch_from_somewhere()}
```

### 2. Add Transform Task
```python
# prefect_poc/tasks/transforms/cleaning.py
@task(name="clean_new_data", tags=["transform"])
def clean_new_data_task(raw_data):
    return process(raw_data)
```

### 3. Use in Flow
```python
# prefect_poc/modular_flow.py
new_data = fetch_new_data_task()
clean_data = clean_new_data_task(new_data)
```

## 🎯 Best Practices

### ✅ DO:
- Organize tasks by domain
- Write unit tests
- Use proper logging
- Add retries for external calls
- Tag tasks appropriately
- Document task purpose

### ❌ DON'T:
- Mix concerns in single task
- Skip error handling
- Forget to test
- Hardcode config values

## 🔄 Development Workflow

```bash
# 1. Make changes
vim prefect_poc/tasks/sources/api.py

# 2. Run tests
pytest tests/test_modular_tasks.py -v

# 3. Test flow locally
python prefect_poc/modular_flow.py

# 4. Create deployment
python prefect_poc/schedule_example.py

# 5. Start worker
prefect worker start --pool default
```

## 📚 Learn More

- [Prefect Docs](https://docs.prefect.io)
- [Task Documentation](https://docs.prefect.io/concepts/tasks/)
- [Flow Documentation](https://docs.prefect.io/concepts/flows/)
- [Deployment Guide](https://docs.prefect.io/concepts/deployments/)

---

**This modular structure makes Prefect comparable to Dagster's organization!** 🚀
