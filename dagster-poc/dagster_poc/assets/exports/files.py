"""Export assets - Save processed data to files."""
import pandas as pd
import os
from dagster import asset, AssetExecutionContext
from typing import Dict


@asset(
    group_name="exports",
    description="Users data exported to CSV",
    compute_kind="csv"
)
def users_csv(context: AssetExecutionContext, users_cleaned: pd.DataFrame) -> str:
    """
    Export users data to CSV file.
    
    Args:
        users_cleaned: Cleaned users DataFrame
        
    Returns:
        Path to the exported CSV file
    """
    output_path = "output/modular_users.csv"
    context.log.info(f"Exporting users data to {output_path}")
    
    os.makedirs("output", exist_ok=True)
    users_cleaned.to_csv(output_path, index=False)
    
    context.log.info(f"Successfully exported {len(users_cleaned)} user records")
    
    return output_path


@asset(
    group_name="exports",
    description="Posts with user info exported to CSV",
    compute_kind="csv"
)
def posts_enriched_csv(
    context: AssetExecutionContext, 
    posts_with_user_info: pd.DataFrame
) -> str:
    """
    Export enriched posts data to CSV file.
    
    Args:
        posts_with_user_info: Enriched posts DataFrame
        
    Returns:
        Path to the exported CSV file
    """
    output_path = "output/modular_posts_enriched.csv"
    context.log.info(f"Exporting enriched posts data to {output_path}")
    
    os.makedirs("output", exist_ok=True)
    posts_with_user_info.to_csv(output_path, index=False)
    
    context.log.info(f"Successfully exported {len(posts_with_user_info)} post records")
    
    return output_path


@asset(
    group_name="exports",
    description="User activity statistics exported to CSV",
    compute_kind="csv"
)
def user_stats_csv(
    context: AssetExecutionContext,
    user_activity_stats: pd.DataFrame
) -> str:
    """
    Export user activity statistics to CSV file.
    
    Args:
        user_activity_stats: User activity statistics DataFrame
        
    Returns:
        Path to the exported CSV file
    """
    output_path = "output/modular_user_stats.csv"
    context.log.info(f"Exporting user statistics to {output_path}")
    
    os.makedirs("output", exist_ok=True)
    user_activity_stats.to_csv(output_path, index=False)
    
    context.log.info(f"Successfully exported statistics for {len(user_activity_stats)} users")
    
    return output_path


@asset(
    group_name="exports",
    description="Top authors exported to CSV",
    compute_kind="csv"
)
def top_authors_csv(
    context: AssetExecutionContext,
    top_authors: pd.DataFrame
) -> str:
    """
    Export top authors to CSV file.
    
    Args:
        top_authors: Top authors DataFrame
        
    Returns:
        Path to the exported CSV file
    """
    output_path = "output/modular_top_authors.csv"
    context.log.info(f"Exporting top authors to {output_path}")
    
    os.makedirs("output", exist_ok=True)
    top_authors.to_csv(output_path, index=False)
    
    context.log.info(f"Successfully exported top {len(top_authors)} authors")
    
    return output_path


@asset(
    group_name="exports",
    description="Final export summary with metadata",
    compute_kind="python"
)
def export_summary(
    context: AssetExecutionContext,
    users_csv: str,
    posts_enriched_csv: str,
    user_stats_csv: str,
    top_authors_csv: str,
    data_summary: Dict
) -> Dict:
    """
    Generate summary of all exports.
    
    Args:
        users_csv: Path to users CSV
        posts_enriched_csv: Path to enriched posts CSV
        user_stats_csv: Path to user stats CSV
        top_authors_csv: Path to top authors CSV
        data_summary: Data summary dictionary
        
    Returns:
        Dictionary with export summary
    """
    context.log.info("Generating export summary...")
    
    summary = {
        "exports": {
            "users": users_csv,
            "posts_enriched": posts_enriched_csv,
            "user_stats": user_stats_csv,
            "top_authors": top_authors_csv
        },
        "data_summary": data_summary,
        "total_files_exported": 4
    }
    
    context.log.info("="*50)
    context.log.info("EXPORT SUMMARY")
    context.log.info("="*50)
    context.log.info("Exported files:")
    for key, path in summary["exports"].items():
        context.log.info(f"  - {key}: {path}")
    context.log.info(f"Total files exported: {summary['total_files_exported']}")
    context.log.info("="*50)
    
    return summary
