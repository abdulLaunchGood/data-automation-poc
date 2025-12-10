"""
Modular assets package for Dagster POC.

This package demonstrates a well-organized, modular asset structure:
- sources/: Data extraction from external APIs
- transforms/: Data cleaning and enrichment
- analytics/: Aggregations and insights
- exports/: File exports and summaries

Each domain has its own subfolder with organized modules.
"""

# Import from nested folder structure
from .sources import api_users_raw, api_posts_raw
from .transforms import users_cleaned, posts_cleaned, posts_with_user_info
from .analytics import user_activity_stats, top_authors, data_summary
from .exports import users_csv, posts_enriched_csv, user_stats_csv, top_authors_csv, export_summary

# List all assets for easy import
ALL_ASSETS = [
    # Sources
    api_users_raw,
    api_posts_raw,
    # Transforms
    users_cleaned,
    posts_cleaned,
    posts_with_user_info,
    # Analytics
    user_activity_stats,
    top_authors,
    data_summary,
    # Exports
    users_csv,
    posts_enriched_csv,
    user_stats_csv,
    top_authors_csv,
    export_summary,
]

__all__ = [
    "ALL_ASSETS",
    # Sources
    "api_users_raw",
    "api_posts_raw",
    # Transforms
    "users_cleaned",
    "posts_cleaned",
    "posts_with_user_info",
    # Analytics
    "user_activity_stats",
    "top_authors",
    "data_summary",
    # Exports
    "users_csv",
    "posts_enriched_csv",
    "user_stats_csv",
    "top_authors_csv",
    "export_summary",
]
