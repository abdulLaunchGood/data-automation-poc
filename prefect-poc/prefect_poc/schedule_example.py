"""
Example of scheduling Prefect flows with deployments.

This demonstrates how to create scheduled deployments for the modular pipeline.
"""
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule, IntervalSchedule
from datetime import timedelta
from prefect_poc.modular_flow import modular_data_pipeline


def create_scheduled_deployments():
    """Create scheduled deployments for the modular pipeline."""
    
    # Deployment 1: Daily at 2 AM
    daily_deployment = Deployment.build_from_flow(
        flow=modular_data_pipeline,
        name="daily-data-refresh",
        description="Daily data refresh at 2 AM",
        schedule=CronSchedule(cron="0 2 * * *", timezone="Asia/Jakarta"),
        work_queue_name="default",
        tags=["production", "daily"]
    )
    
    # Deployment 2: Every 6 hours
    six_hourly_deployment = Deployment.build_from_flow(
        flow=modular_data_pipeline,
        name="six-hourly-refresh",
        description="Refresh data every 6 hours",
        schedule=CronSchedule(cron="0 */6 * * *", timezone="Asia/Jakarta"),
        work_queue_name="default",
        tags=["production", "frequent"]
    )
    
    # Deployment 3: Every hour (using IntervalSchedule)
    hourly_deployment = Deployment.build_from_flow(
        flow=modular_data_pipeline,
        name="hourly-refresh",
        description="Refresh data every hour",
        schedule=IntervalSchedule(interval=timedelta(hours=1)),
        work_queue_name="default",
        tags=["production", "hourly"]
    )
    
    # Deployment 4: Business hours (9 AM - 5 PM, Mon-Fri)
    business_hours_deployment = Deployment.build_from_flow(
        flow=modular_data_pipeline,
        name="business-hours-refresh",
        description="Refresh during business hours",
        schedule=CronSchedule(cron="0 9-17 * * 1-5", timezone="Asia/Jakarta"),
        work_queue_name="default",
        tags=["production", "business-hours"]
    )
    
    return [
        daily_deployment,
        six_hourly_deployment,
        hourly_deployment,
        business_hours_deployment
    ]


def apply_deployments():
    """Apply all deployments to the server."""
    print("Creating scheduled deployments...")
    
    deployments = create_scheduled_deployments()
    
    for deployment in deployments:
        deployment_id = deployment.apply()
        print(f"✅ Created: {deployment.name}")
        print(f"   Schedule: {deployment.schedule}")
        print(f"   ID: {deployment_id}\n")
    
    print("="*60)
    print("All deployments created successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start Prefect server: prefect server start")
    print("2. Start worker: prefect worker start --pool default")
    print("3. Deployments will run automatically per schedule")


if __name__ == "__main__":
    apply_deployments()
