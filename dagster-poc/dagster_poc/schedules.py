"""Schedules for Dagster assets."""
from dagster import (
    AssetSelection,
    ScheduleDefinition,
    define_asset_job,
)

# Define a job that selects specific assets to run
daily_data_refresh_job = define_asset_job(
    name="daily_data_refresh",
    selection=AssetSelection.all(),  # or select specific assets
    description="Daily job to refresh all data assets"
)

# Schedule to run daily at 2 AM
daily_schedule = ScheduleDefinition(
    name="daily_data_refresh_schedule",
    job=daily_data_refresh_job,
    cron_schedule="0 2 * * *",  # Every day at 2 AM
    description="Runs daily data refresh at 2 AM"
)

# Schedule for just source assets (every 6 hours)
source_refresh_job = define_asset_job(
    name="source_refresh",
    selection=AssetSelection.groups("sources"),  # Only sources group
    description="Refresh source data"
)

source_refresh_schedule = ScheduleDefinition(
    name="source_refresh_schedule",
    job=source_refresh_job,
    cron_schedule="0 */6 * * *",  # Every 6 hours
    description="Refreshes source data every 6 hours"
)

# Schedule for analytics (every hour)
analytics_job = define_asset_job(
    name="analytics_refresh",
    selection=AssetSelection.groups("analytics", "exports"),
    description="Refresh analytics and exports"
)

analytics_schedule = ScheduleDefinition(
    name="analytics_schedule",
    job=analytics_job,
    cron_schedule="0 * * * *",  # Every hour
    description="Refreshes analytics every hour"
)

# Export all schedules
ALL_SCHEDULES = [
    daily_schedule,
    source_refresh_schedule,
    analytics_schedule,
]
