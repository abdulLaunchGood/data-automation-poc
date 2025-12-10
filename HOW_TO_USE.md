# How to Use This POC

Complete guide to running and understanding the Dagster vs Prefect data automation POC.

---

## 📦 Quick Start

### 1. **Choose Your Implementation**

This POC contains two implementations:
- **dagster-poc/** - Modern asset-based approach (RECOMMENDED)
- **prefect-poc/** - Simple task-flow approach

---

## 🚀 Running Dagster

### Installation

```bash
cd dagster-poc
pip install -e ".[dev]"
```

### Start Dagster UI

```bash
dagster dev
```

This will:
- Start the Dagster web server
- Open UI at **http://localhost:3000**
- Load all 17 assets and schedules

### Using the UI

#### 1. **View Assets**
- Click **"Assets"** tab
- See beautiful lineage graph
- View 4 groups: sources, transforms, analytics, exports

#### 2. **Materialize Assets**
```
Option A: Materialize All
- Click "Materialize all" button
- All assets execute in dependency order
- Watch progress in real-time

Option B: Materialize Individual
- Click any asset
- Click "Materialize" button
- Only that asset + dependencies run

Option C: Materialize by Group
- Select "sources" group
- Materialize only source assets
```

#### 3. **View Results**
- Check `dagster-poc/output/` directory
- CSV files generated:
  - `modular_users.csv`
  - `modular_posts_enriched.csv`
  - `modular_user_stats.csv`
  - `modular_top_authors.csv`

#### 4. **Enable Schedules**
- Click **"Overview"** → **"Schedules"**
- Toggle schedules ON:
  - `daily_data_refresh_schedule` (2 AM daily)
  - `source_refresh_schedule` (Every 6 hours)
  - `analytics_schedule` (Every hour)
- Schedules run automatically

#### 5. **View Logs**
- Click any asset
- Go to "Latest materialization"
- See execution logs and context

---

## 🎯 Running Prefect

### Installation

```bash
cd prefect-poc
pip install -e ".[dev]"
```

### Run the Flow (NO SERVER NEEDED!)

```bash
python prefect_poc/flows.py
```

Output:
```
Starting data extraction flow...
Fetching data from API...
Fetched 10 users from API
Processing data...
Saving to CSV...
Data saved to output/prefect_users.csv
Flow completed successfully!
```

**That's it! No server required for basic usage!** ✅

### Using Prefect UI (Optional - Requires Server)

If you want the web UI, you have two options:

**Option 1: Local Server (Free)**
```bash
# Terminal 1: Start Prefect server
prefect server start

# Terminal 2: Run flow with UI tracking
python prefect_poc/flows.py
```

Access UI at **http://localhost:4200**

**Option 2: Prefect Cloud (Free tier available)**
```bash
# Sign up at https://app.prefect.cloud
prefect cloud login
python prefect_poc/flows.py
```

Access UI at **https://app.prefect.cloud**

**Key Difference:**
- **Dagster:** Server REQUIRED (for UI and execution)
- **Prefect:** Server OPTIONAL (can run directly without it)

### Scheduling Prefect Flows

Prefect uses **Deployments** for scheduling. You need a server running.

**Step 1: Create a Deployment**

```python
# prefect_poc/flows.py - Add at the end
if __name__ == "__main__":
    from prefect.deployments import Deployment
    from prefect.server.schemas.schedules import CronSchedule
    
    # Create deployment with schedule
    deployment = Deployment.build_from_flow(
        flow=data_extraction_flow,
        name="daily-data-extraction",
        schedule=CronSchedule(cron="0 2 * * *"),  # Daily at 2 AM
        work_queue_name="default"
    )
    
    deployment.apply()
    print("Deployment created!")
```

**Step 2: Start Prefect Server**

```bash
# Terminal 1: Start server
prefect server start
```

**Step 3: Create & Apply Deployment**

```bash
# Terminal 2: Create deployment
cd prefect-poc
python prefect_poc/flows.py
```

**Step 4: Start Worker**

```bash
# Terminal 3: Start worker to execute scheduled runs
prefect worker start --pool default
```

**Alternative: Quick Deployment via CLI**

```bash
# Simpler method
prefect deployment build prefect_poc/flows.py:data_extraction_flow \
    --name "daily-extraction" \
    --cron "0 2 * * *" \
    --apply

# Start worker
prefect worker start --pool default
```

**Common Schedules:**
```python
# Every hour
CronSchedule(cron="0 * * * *")

# Every 6 hours
CronSchedule(cron="0 */6 * * *")

# Business hours (9 AM - 5 PM, Mon-Fri)
CronSchedule(cron="0 9-17 * * 1-5")

# Every day at 2 AM
CronSchedule(cron="0 2 * * *")
```

**Using Prefect Cloud (Easier):**

```bash
# 1. Sign up at https://app.prefect.cloud
# 2. Login
prefect cloud login

# 3. Create deployment (cloud handles workers!)
prefect deployment build prefect_poc/flows.py:data_extraction_flow \
    --name "production-pipeline" \
    --cron "0 2 * * *" \
    --apply
```

**Key Differences from Dagster:**
- **Dagster:** Schedules built into platform (easier)
- **Prefect:** Need deployments + workers (more flexible)
- **Prefect Cloud:** Managed workers (easiest)

---

## 🧪 Running Tests

### Dagster Tests

```bash
cd dagster-poc
pytest tests/ -v
```

### Prefect Tests

```bash
cd prefect-poc
pytest tests/ -v
```

---

## 📚 Understanding the Code

### Dagster Structure

```
dagster-poc/
├── dagster_poc/
│   ├── __init__.py           # Main entry point with Definitions
│   ├── assets/               # Asset-based pipelines (MAIN)
│   │   ├── sources/          # Data extraction
│   │   │   └── api.py        # API calls
│   │   ├── transforms/       # Data cleaning
│   │   │   └── cleaning.py   # Transformations
│   │   ├── analytics/        # Aggregations
│   │   │   └── stats.py      # Analytics
│   │   └── exports/          # File exports
│   │       └── files.py      # CSV generation
│   ├── schedules.py          # Asset schedules
│   ├── simple_assets.py      # Simple examples
│   ├── jobs.py              # Traditional jobs (legacy)
│   └── ops.py               # Traditional ops (legacy)
└── tests/                   # Unit tests
```

### Prefect Structure

```
prefect-poc/
├── prefect_poc/
│   ├── __init__.py
│   ├── tasks.py    # Task definitions
│   └── flows.py    # Flow orchestration
└── tests/          # Unit tests
```

---

## 🎨 Key Concepts

### Dagster Assets (Recommended)

**What are Assets?**
- Data products you want to create
- Focus on WHAT (not HOW)
- Automatic dependency tracking

**Example:**
```python
@asset
def api_users_raw(context):
    """Fetch users from API"""
    return fetch_from_api()

@asset
def users_cleaned(context, api_users_raw):
    """Clean users - depends on api_users_raw"""
    return clean(api_users_raw)
```

**Dependencies are automatic** based on parameter names!

### Dagster Jobs & Ops (Traditional)

**What are Ops?**
- Computational steps
- Focus on HOW
- Manual wiring required

**Example:**
```python
@op
def fetch_data(context):
    return fetch()

@job
def my_pipeline():
    data = fetch_data()
    process_data(data)
```

### Prefect Tasks & Flows

**Simple and intuitive:**
```python
@task
def extract():
    return fetch_data()

@task
def transform(data):
    return clean(data)

@flow
def my_flow():
    data = extract()
    clean_data = transform(data)
```

---

## 💡 Common Use Cases

### 1. **Add New API Source**

```python
# dagster_poc/assets/sources/api.py
@asset(group_name="sources")
def new_api_data(context):
    """Fetch from new API"""
    response = requests.get("https://api.example.com/data")
    return response.json()
```

### 2. **Add Transformation**

```python
# dagster_poc/assets/transforms/cleaning.py
@asset(group_name="transforms")
def new_transform(context, new_api_data):
    """Transform new data"""
    df = pd.DataFrame(new_api_data)
    return df[df['status'] == 'active']
```

### 3. **Add Analytics**

```python
# dagster_poc/assets/analytics/stats.py
@asset(group_name="analytics")
def new_metrics(context, new_transform):
    """Calculate metrics"""
    return {
        'total': len(new_transform),
        'avg_value': new_transform['value'].mean()
    }
```

### 4. **Export to File**

```python
# dagster_poc/assets/exports/files.py
@asset(group_name="exports")
def new_export(context, new_metrics):
    """Export to CSV"""
    df = pd.DataFrame([new_metrics])
    df.to_csv('output/metrics.csv')
    return 'output/metrics.csv'
```

### 5. **Schedule New Assets**

```python
# dagster_poc/schedules.py
new_job = define_asset_job(
    name="new_refresh",
    selection=AssetSelection.keys("new_api_data", "new_transform")
)

new_schedule = ScheduleDefinition(
    name="new_schedule",
    job=new_job,
    cron_schedule="0 */2 * * *"  # Every 2 hours
)
```

---

## 🔧 Customization

### Change API Endpoint

Edit `dagster_poc/assets/sources/api.py`:
```python
API_URL = "https://your-api.com/endpoint"
```

### Change Output Directory

Edit asset files:
```python
output_path = "your/custom/path/file.csv"
```

### Add Database Connection

```python
from sqlalchemy import create_engine

@asset
def database_data(context):
    engine = create_engine("postgresql://user:pass@host/db")
    return pd.read_sql("SELECT * FROM table", engine)
```

### Handle Large Data

```python
@asset
def big_table(context):
    engine = create_engine("mysql://...")
    
    # Aggregate in database
    query = """
    SELECT date, COUNT(*) as count
    FROM large_table
    GROUP BY date
    """
    return pd.read_sql(query, engine)  # Small result!
```

---

## 📊 Monitoring & Debugging

### View Asset Status
```
UI → Assets → Click any asset
- See last materialization time
- View execution logs
- Check dependencies
```

### Debug Failed Assets
```
1. Click failed asset
2. Go to "Latest run"
3. Read error logs
4. Fix code
5. Re-materialize
```

### Check Lineage
```
UI → Assets → View graph
- See data flow
- Understand dependencies
- Identify bottlenecks
```

---

## 🚨 Troubleshooting

### Problem: "Module not found"
```bash
# Solution: Install in dev mode
pip install -e ".[dev]"
```

### Problem: "Port already in use"
```bash
# Solution: Change port
dagster dev -p 3001
```

### Problem: "Asset not updating"
```bash
# Solution: Clear cache
rm -rf .dagster/storage/
dagster dev
```

### Problem: "Import errors"
```bash
# Solution: Check pyproject.toml
[tool.dagster]
module_name = "dagster_poc"
```

---

## 🎯 Best Practices

### ✅ DO:
- Use **Assets** for data pipelines
- Organize by **domain** (sources, transforms, etc.)
- Write **unit tests**
- Use **asset groups**
- Monitor in **UI**
- Use **SQL pushdown** for large data
- Document with **descriptions**

### ❌ DON'T:
- Load entire tables into memory
- Mix assets and ops unnecessarily
- Skip testing
- Ignore failed runs
- Over-schedule
- Create circular dependencies

---

## 📈 Performance Tips

### 1. **Caching**
Dagster automatically caches results - downstream assets use cache!

### 2. **Partitioning**
```python
from dagster import DailyPartitionsDefinition

daily = DailyPartitionsDefinition(start_date="2024-01-01")

@asset(partitions_def=daily)
def daily_data(context):
    date = context.partition_key
    # Process one day at a time
```

### 3. **Parallel Execution**
Assets without dependencies run in parallel automatically!

### 4. **SQL Pushdown**
```python
# ✅ Good - aggregate in database
query = "SELECT customer_id, SUM(amount) FROM orders GROUP BY customer_id"
df = pd.read_sql(query, engine)

# ❌ Bad - load everything
df = pd.read_sql("SELECT * FROM orders", engine)
```

---

## 🔄 Development Workflow

```bash
# 1. Make changes to code
vim dagster_poc/assets/sources/api.py

# 2. Dagster auto-reloads (no restart needed!)

# 3. Materialize in UI to test

# 4. View logs and results

# 5. Write tests
vim tests/test_assets.py

# 6. Run tests
pytest tests/

# 7. Commit
git add .
git commit -m "Added new feature"
```

---

## 📚 Next Steps

### Learn More:
- Read `DAGSTER_PROS_CONS.md` for detailed comparison
- Check official docs: https://docs.dagster.io
- Take Dagster University: https://courses.dagster.io

### Extend the POC:
1. Add database connections
2. Integrate with cloud storage (S3, GCS)
3. Add data quality checks
4. Create custom I/O managers
5. Deploy to production

### Deploy:
```bash
# Using Docker
docker build -t my-dagster-app .
docker run -p 3000:3000 my-dagster-app

# Using Dagster Cloud (managed)
dagster-cloud deployment deploy
```

---

## 🎊 Summary

**Quick Commands:**
```bash
# Run Dagster
cd dagster-poc && dagster dev

# Run Prefect
cd prefect-poc && python prefect_poc/flows.py

# Run Tests
pytest tests/
```

**Key URLs:**
- Dagster UI: http://localhost:3000
- Prefect UI: http://localhost:4200

**Support:**
- Dagster Slack: https://dagster.io/slack
- Dagster Docs: https://docs.dagster.io
- Prefect Docs: https://docs.prefect.io

---

**You're ready to build production data pipelines!** 🚀
