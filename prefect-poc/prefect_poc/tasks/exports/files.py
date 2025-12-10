"""File export tasks."""
import os
from prefect import task
from prefect.logging import get_run_logger


@task(name="export_users_csv", tags=["export", "csv"])
def export_users_task(users_data, output_dir="output"):
    """Export users data to CSV."""
    logger = get_run_logger()
    
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "prefect_modular_users.csv")
    
    logger.info(f"Exporting {len(users_data)} users to {filepath}")
    users_data.to_csv(filepath, index=False)
    logger.info(f"Successfully exported to {filepath}")
    
    return filepath


@task(name="export_posts_csv", tags=["export", "csv"])
def export_posts_task(posts_data, output_dir="output"):
    """Export enriched posts to CSV."""
    logger = get_run_logger()
    
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "prefect_modular_posts_enriched.csv")
    
    logger.info(f"Exporting {len(posts_data)} posts to {filepath}")
    posts_data.to_csv(filepath, index=False)
    logger.info(f"Successfully exported to {filepath}")
    
    return filepath


@task(name="export_user_stats_csv", tags=["export", "csv"])
def export_user_stats_task(user_stats, output_dir="output"):
    """Export user activity statistics to CSV."""
    logger = get_run_logger()
    
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "prefect_modular_user_stats.csv")
    
    logger.info(f"Exporting user stats to {filepath}")
    user_stats.to_csv(filepath, index=False)
    logger.info(f"Successfully exported to {filepath}")
    
    return filepath


@task(name="export_top_authors_csv", tags=["export", "csv"])
def export_top_authors_task(top_authors, output_dir="output"):
    """Export top authors to CSV."""
    logger = get_run_logger()
    
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "prefect_modular_top_authors.csv")
    
    logger.info(f"Exporting top {len(top_authors)} authors to {filepath}")
    top_authors.to_csv(filepath, index=False)
    logger.info(f"Successfully exported to {filepath}")
    
    return filepath


@task(name="export_summary_csv", tags=["export", "csv"])
def export_summary_task(summary, output_dir="output"):
    """Export data summary to CSV."""
    logger = get_run_logger()
    
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "prefect_modular_summary.csv")
    
    logger.info(f"Exporting summary to {filepath}")
    summary.to_csv(filepath, index=False)
    logger.info(f"Successfully exported to {filepath}")
    
    return filepath
