"""Transform assets - Data transformation and enrichment."""
import pandas as pd
from dagster import asset, AssetExecutionContext
from typing import Dict


@asset(
    group_name="transforms",
    description="Cleaned and structured user data",
    compute_kind="pandas"
)
def users_cleaned(context: AssetExecutionContext, api_users_raw: Dict) -> pd.DataFrame:
    """
    Transform raw user data into a clean DataFrame.
    
    Extracts key fields and structures the data.
    
    Args:
        api_users_raw: Raw user data from API
        
    Returns:
        DataFrame with cleaned user data
    """
    context.log.info("Transforming raw user data...")
    
    users = api_users_raw["data"]
    cleaned_records = []
    
    for user in users:
        cleaned_records.append({
            "user_id": user["id"],
            "name": user["name"],
            "username": user["username"],
            "email": user["email"],
            "city": user["address"]["city"],
            "company": user["company"]["name"],
            "website": user.get("website", "N/A")
        })
    
    df = pd.DataFrame(cleaned_records)
    context.log.info(f"Transformed {len(df)} user records")
    
    return df


@asset(
    group_name="transforms",
    description="Cleaned and structured posts data",
    compute_kind="pandas"
)
def posts_cleaned(context: AssetExecutionContext, api_posts_raw: Dict) -> pd.DataFrame:
    """
    Transform raw posts data into a clean DataFrame.
    
    Args:
        api_posts_raw: Raw posts data from API
        
    Returns:
        DataFrame with cleaned posts data
    """
    context.log.info("Transforming raw posts data...")
    
    posts = api_posts_raw["data"]
    cleaned_records = []
    
    for post in posts:
        cleaned_records.append({
            "post_id": post["id"],
            "user_id": post["userId"],
            "title": post["title"],
            "body": post["body"],
            "title_length": len(post["title"]),
            "body_length": len(post["body"])
        })
    
    df = pd.DataFrame(cleaned_records)
    context.log.info(f"Transformed {len(df)} post records")
    
    return df


@asset(
    group_name="transforms",
    description="Enriched posts with user information",
    compute_kind="pandas"
)
def posts_with_user_info(
    context: AssetExecutionContext, 
    posts_cleaned: pd.DataFrame, 
    users_cleaned: pd.DataFrame
) -> pd.DataFrame:
    """
    Enrich posts data with user information.
    
    Joins posts with users to add author details.
    
    Args:
        posts_cleaned: Cleaned posts DataFrame
        users_cleaned: Cleaned users DataFrame
        
    Returns:
        DataFrame with posts enriched with user info
    """
    context.log.info("Enriching posts with user information...")
    
    # Merge posts with users
    enriched = posts_cleaned.merge(
        users_cleaned[["user_id", "name", "username", "company"]],
        on="user_id",
        how="left"
    )
    
    # Rename columns for clarity
    enriched = enriched.rename(columns={
        "name": "author_name",
        "username": "author_username",
        "company": "author_company"
    })
    
    context.log.info(f"Enriched {len(enriched)} post records with user information")
    
    return enriched
