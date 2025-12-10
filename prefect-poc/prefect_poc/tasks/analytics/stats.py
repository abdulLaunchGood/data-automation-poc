"""Analytics and statistics tasks."""
import pandas as pd
from prefect import task
from prefect.logging import get_run_logger


@task(name="user_activity_stats", tags=["analytics", "stats"])
def user_activity_task(posts_cleaned, users_cleaned):
    """Calculate user activity statistics."""
    logger = get_run_logger()
    
    logger.info("Calculating user activity statistics")
    
    # Count posts per user
    post_counts = posts_cleaned.groupby('userId').size().reset_index(name='post_count')
    
    # Merge with user data
    stats = users_cleaned.merge(post_counts, left_on='id', right_on='userId', how='left')
    stats['post_count'] = stats['post_count'].fillna(0).astype(int)
    
    # Calculate average post length per user
    avg_length = posts_cleaned.groupby('userId')['body_length'].mean().reset_index(name='avg_post_length')
    stats = stats.merge(avg_length, left_on='id', right_on='userId', how='left')
    stats['avg_post_length'] = stats['avg_post_length'].fillna(0).round(2)
    
    logger.info(f"Calculated stats for {len(stats)} users")
    
    return stats[['id', 'name', 'email', 'post_count', 'avg_post_length']]


@task(name="top_authors", tags=["analytics", "ranking"])
def top_authors_task(user_stats):
    """Identify top authors by post count."""
    logger = get_run_logger()
    
    logger.info("Identifying top authors")
    
    # Sort by post count and get top 10
    top = user_stats.nlargest(10, 'post_count')
    
    logger.info(f"Found top {len(top)} authors")
    
    return top


@task(name="data_summary", tags=["analytics", "summary"])
def summary_task(users_cleaned, posts_cleaned, posts_enriched):
    """Generate overall data summary."""
    logger = get_run_logger()
    
    logger.info("Generating data summary")
    
    summary = {
        'total_users': len(users_cleaned),
        'total_posts': len(posts_cleaned),
        'total_enriched': len(posts_enriched),
        'avg_posts_per_user': round(len(posts_cleaned) / len(users_cleaned), 2),
        'avg_title_length': round(posts_cleaned['title_length'].mean(), 2),
        'avg_body_length': round(posts_cleaned['body_length'].mean(), 2),
    }
    
    logger.info(f"Summary: {summary}")
    
    return pd.DataFrame([summary])
