"""Analytics assets - Data aggregations and insights."""
import pandas as pd
from dagster import asset, AssetExecutionContext
from typing import Dict


@asset(
    group_name="analytics",
    description="User activity statistics",
    compute_kind="pandas"
)
def user_activity_stats(
    context: AssetExecutionContext,
    users_cleaned: pd.DataFrame,
    posts_cleaned: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate activity statistics per user.
    
    Args:
        users_cleaned: Cleaned users DataFrame
        posts_cleaned: Cleaned posts DataFrame
        
    Returns:
        DataFrame with user activity statistics
    """
    context.log.info("Calculating user activity statistics...")
    
    # Count posts per user
    post_counts = posts_cleaned.groupby("user_id").agg({
        "post_id": "count",
        "title_length": "mean",
        "body_length": "mean"
    }).reset_index()
    
    post_counts.columns = ["user_id", "total_posts", "avg_title_length", "avg_body_length"]
    
    # Merge with user info
    stats = users_cleaned.merge(post_counts, on="user_id", how="left")
    stats["total_posts"] = stats["total_posts"].fillna(0).astype(int)
    
    context.log.info(f"Generated activity stats for {len(stats)} users")
    
    return stats


@asset(
    group_name="analytics",
    description="Top authors by post count",
    compute_kind="pandas"
)
def top_authors(
    context: AssetExecutionContext,
    user_activity_stats: pd.DataFrame
) -> pd.DataFrame:
    """
    Identify top authors by post count.
    
    Args:
        user_activity_stats: User activity statistics
        
    Returns:
        DataFrame with top 5 authors
    """
    context.log.info("Identifying top authors...")
    
    top = user_activity_stats.nlargest(5, "total_posts")[
        ["user_id", "name", "username", "company", "total_posts", "avg_title_length"]
    ]
    
    context.log.info(f"Identified top {len(top)} authors")
    
    return top


@asset(
    group_name="analytics",
    description="Summary statistics for the entire dataset",
    compute_kind="python"
)
def data_summary(
    context: AssetExecutionContext,
    users_cleaned: pd.DataFrame,
    posts_cleaned: pd.DataFrame,
    posts_with_user_info: pd.DataFrame
) -> Dict:
    """
    Generate overall data summary.
    
    Args:
        users_cleaned: Cleaned users DataFrame
        posts_cleaned: Cleaned posts DataFrame
        posts_with_user_info: Enriched posts DataFrame
        
    Returns:
        Dictionary with summary statistics
    """
    context.log.info("Generating data summary...")
    
    summary = {
        "total_users": len(users_cleaned),
        "total_posts": len(posts_cleaned),
        "enriched_posts": len(posts_with_user_info),
        "unique_companies": users_cleaned["company"].nunique(),
        "unique_cities": users_cleaned["city"].nunique(),
        "avg_posts_per_user": round(len(posts_cleaned) / len(users_cleaned), 2),
        "avg_title_length": round(posts_cleaned["title_length"].mean(), 2),
        "avg_body_length": round(posts_cleaned["body_length"].mean(), 2)
    }
    
    context.log.info("="*50)
    context.log.info("DATA SUMMARY")
    context.log.info("="*50)
    for key, value in summary.items():
        context.log.info(f"{key}: {value}")
    context.log.info("="*50)
    
    return summary
