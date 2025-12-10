# Asset Scheduling in Dagster

## YES! Assets CAN Have Schedules! ✅

Assets in Dagster can absolutely be scheduled - in fact, this is one of Dagster's most powerful features!

## How It Works

You don't schedule assets directly. Instead, you:
1. **Define an Asset Job** - Select which assets to run
2. **Create a Schedule** - Attach schedule to the job
3. **Dagster runs the job** - Which materializes the selected assets

## Example from the POC

```python
# schedules.py
from dagster import AssetSelection, ScheduleDefinition, define_asset_job

# Step 1: Define job that selects assets
daily_data_refresh_job = define_asset_job(
    name="daily_data_refresh",
    selection=AssetSelection.all(),  # All assets
    description="Daily job to refresh all data assets"
)

# Step 2: Create schedule for the job
daily_schedule = ScheduleDefinition(
    name="daily_data_refresh_schedule",
    job=daily_data_refresh_job,
    cron_schedule="0 2 * * *",  # Every day at 2 AM
    description="Runs daily data refresh at 2 AM"
)
```

## Asset Selection Options

### 1. **All Assets**
```python
selection=AssetSelection.all()
# Materializes ALL assets in your project
```

### 2. **By Group**
```python
selection=AssetSelection.groups("sources")
# Only assets in the "sources" group

selection=AssetSelection.groups("analytics", "exports")
# Assets in multiple groups
```

### 3. **By Key**
```python
selection=AssetSelection.keys("mysql_orders", "users_cleaned")
# Specific assets by name
```

### 4. **Upstream/Downstream**
```python
selection=AssetSelection.keys("mysql_orders").downstream()
# mysql_orders AND everything that depends on it

selection=AssetSelection.keys("user_stats_csv").upstream()
# Everything needed to create user_stats_csv
```

### 5. **Complex Selections**
```python
selection=(
    AssetSelection.groups("sources")  # Source assets
    | AssetSelection.groups("transforms")  # OR transform assets
)

selection=(
    AssetSelection.groups("analytics")  # Analytics assets
    & AssetSelection.keys("top_authors").upstream()  # AND their dependencies
)
```

## Complete Scheduling Examples

### Schedule 1: Daily Full Refresh (2 AM)

```python
daily_job = define_asset_job(
    name="daily_refresh",
    selection=AssetSelection.all()
)

daily_schedule = ScheduleDefinition(
    name="daily_schedule",
    job=daily_job,
    cron_schedule="0 2 * * *"  # 2 AM daily
)
```

### Schedule 2: Hourly Source Refresh

```python
source_job = define_asset_job(
    name="source_refresh",
    selection=AssetSelection.groups("sources")
)

hourly_schedule = ScheduleDefinition(
    name="hourly_sources",
    job=source_job,
    cron_schedule="0 * * * *"  # Every hour
)
```

### Schedule 3: Business Hours Analytics (9 AM - 5 PM)

```python
analytics_job = define_asset_job(
    name="analytics_refresh",
    selection=AssetSelection.groups("analytics", "exports")
)

business_hours_schedule = ScheduleDefinition(
    name="business_hours_analytics",
    job=analytics_job,
    cron_schedule="0 9-17 * * 1-5"  # 9AM-5PM, Mon-Fri
)
```

### Schedule 4: Weekend Batch Processing

```python
weekend_job = define_asset_job(
    name="weekend_batch",
    selection=AssetSelection.all()
)

weekend_schedule = ScheduleDefinition(
    name="weekend_processing",
    job=weekend_job,
    cron_schedule="0 0 * * 0,6"  # Midnight on Sat & Sun
)
```

## Cron Schedule Cheat Sheet

```
 ┌───────────── minute (0 - 59)
 │ ┌───────────── hour (0 - 23)
 │ │ ┌───────────── day of month (1 - 31)
 │ │ │ ┌───────────── month (1 - 12)
 │ │ │ │ ┌───────────── day of week (0 - 6) (0=Sunday)
 │ │ │ │ │
 * * * * *

Common patterns:
0 * * * *       → Every hour
0 0 * * *       → Daily at midnight
0 2 * * *       → Daily at 2 AM
0 */6 * * *     → Every 6 hours
0 9-17 * * 1-5  → Business hours (Mon-Fri)
*/15 * * * *    → Every 15 minutes
0 0 * * 0       → Weekly on Sunday
0 0 1 * *       → Monthly on 1st
```

## Register Schedules in Definitions

```python
# __init__.py
from dagster import Definitions
from .schedules import ALL_SCHEDULES

defs = Definitions(
    assets=[...],
    schedules=ALL_SCHEDULES  # Register schedules here!
)
```

## View & Control Schedules in UI

Once registered, go to Dagster UI:

1. **Overview Tab** → See all schedules
2. **Toggle On/Off** → Enable/disable schedules
3. **View Runs** → See schedule execution history
4. **Test Run** → Manually trigger a scheduled job

## Sensors (Event-Based Alternative)

Besides time-based schedules, Dagster also supports **Sensors** for event-based triggers:

```python
from dagster import sensor, RunRequest, SensorDefinition

@sensor(job=daily_data_refresh_job)
def file_sensor(context):
    """Trigger when new file appears"""
    if new_file_detected():
        return RunRequest(
            run_key=f"file_{timestamp}",
            tags={"source": "file_sensor"}
        )
```

## Freshness Policies (Automatic Scheduling)

For even simpler scheduling, use Freshness Policies:

```python
from dagster import asset, FreshnessPolicy

@asset(
    freshness_policy=FreshnessPolicy(
        maximum_lag_minutes=60  # Must be refreshed within 1 hour
    )
)
def mysql_orders(context):
    """Dagster auto-schedules to maintain freshness"""
    return pd.read_sql("SELECT * FROM orders", engine)
```

Dagster will automatically schedule this asset to ensure it's never stale!

## Our POC Schedules

The POC includes 3 schedules:

### 1. Daily Full Refresh
- **When**: 2 AM daily
- **What**: All assets
- **Use case**: Complete data refresh overnight

### 2. Source Refresh
- **When**: Every 6 hours
- **What**: Source assets only
- **Use case**: Keep raw data updated

### 3. Analytics Refresh
- **When**: Every hour
- **What**: Analytics + Exports
- **Use case**: Fresh dashboards/reports

## Testing Schedules

### In UI:
1. Go to **Overview** → **Schedules**
2. Find your schedule
3. Click **"Test Schedule"**
4. Trigger immediately without waiting

### Programmatically:
```python
# In tests or scripts
from dagster import build_schedule_context

context = build_schedule_context()
schedule.evaluate_tick(context)
```

## Best Practices

### ✅ DO:
- Schedule sources more frequently than transforms
- Use cron schedules for predictable loads
- Group related assets in one schedule
- Monitor schedule execution in UI

### ❌ DON'T:
- Schedule every single asset separately (use groups!)
- Over-schedule (unnecessary compute costs)
- Forget to enable schedules in UI
- Ignore failed schedule runs

## Key Takeaway 🎯

**YES - Assets can have schedules!**

1. Create **Asset Job** with `define_asset_job()`
2. Select assets with **AssetSelection**
3. Define **Schedule** with cron expression
4. Register in **Definitions**
5. Enable in **Dagster UI**

Assets + Schedules = Automated Data Pipelines! 🚀

---

**Your POC now has 3 schedules ready to use!**

Enable them in the UI and watch your assets materialize automatically!
