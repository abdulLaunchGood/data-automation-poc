"""Data cleaning and enrichment tasks."""
import pandas as pd
from prefect import task
from prefect.logging import get_run_logger


@task(name="clean_users", tags=["transform", "cleaning"])
def clean_users_task(users_raw):
    """Clean and normalize users data."""
    logger = get_run_logger()
    
    df = pd.DataFrame(users_raw["data"])
    logger.info(f"Cleaning {len(df)} users")
    
    # Keep only essential fields
    cleaned = df[[
        'id', 'name', 'username', 'email',
        'phone', 'website'
    ]].copy()
    
    # Normalize email
    cleaned['email'] = cleaned['email'].str.lower()
    
    # Add full_name
    cleaned['full_name'] = cleaned['name']
    
    logger.info(f"Cleaned {len(cleaned)} users successfully")
    
    return cleaned


@task(name="clean_posts", tags=["transform", "cleaning"])
def clean_posts_task(posts_raw):
    """Clean and normalize posts data."""
    logger = get_run_logger()
    
    df = pd.DataFrame(posts_raw["data"])
    logger.info(f"Cleaning {len(df)} posts")
    
    # Clean text fields
    cleaned = df.copy()
    cleaned['title'] = cleaned['title'].str.strip()
    cleaned['body'] = cleaned['body'].str.strip()
    
    # Add title length
    cleaned['title_length'] = cleaned['title'].str.len()
    cleaned['body_length'] = cleaned['body'].str.len()
    
    logger.info(f"Cleaned {len(cleaned)} posts successfully")
    
    return cleaned


@task(name="enrich_posts", tags=["transform", "enrichment"])
def enrich_posts_task(posts_cleaned, users_cleaned):
    """Enrich posts with user information."""
    logger = get_run_logger()
    
    logger.info("Enriching posts with user data")
    
    # Merge posts with users
    enriched = posts_cleaned.merge(
        users_cleaned[['id', 'name', 'email']],
        left_on='userId',
        right_on='id',
        suffixes=('_post', '_user')
    )
    
    # Rename columns for clarity
    enriched = enriched.rename(columns={
        'name': 'author_name',
        'email': 'author_email'
    })
    
    logger.info(f"Enriched {len(enriched)} posts with user data")
    
    return enriched
