"""
Modular data extraction flow - Production-ready structure.

This flow demonstrates a clean, modular organization similar to Dagster's assets,
organized by domain (sources, transforms, analytics, exports).
"""
from prefect import flow
from prefect.logging import get_run_logger

# Import tasks from modular structure
from prefect_poc.tasks.sources import fetch_users_task, fetch_posts_task
from prefect_poc.tasks.transforms import clean_users_task, clean_posts_task, enrich_posts_task
from prefect_poc.tasks.analytics import user_activity_task, top_authors_task, summary_task
from prefect_poc.tasks.exports import (
    export_users_task,
    export_posts_task,
    export_user_stats_task,
    export_top_authors_task,
    export_summary_task
)


@flow(name="modular-data-pipeline", log_prints=True)
def modular_data_pipeline():
    """
    Complete data pipeline with modular task organization.
    
    Pipeline stages:
    1. Sources: Fetch data from APIs
    2. Transforms: Clean and enrich data
    3. Analytics: Calculate statistics
    4. Exports: Save to CSV files
    """
    logger = get_run_logger()
    logger.info("="*60)
    logger.info("Starting Modular Data Pipeline")
    logger.info("="*60)
    
    # ========== STAGE 1: DATA SOURCES ==========
    logger.info("\n📥 STAGE 1: Data Extraction")
    users_raw = fetch_users_task()
    posts_raw = fetch_posts_task()
    
    # ========== STAGE 2: DATA TRANSFORMATION ==========
    logger.info("\n🔄 STAGE 2: Data Transformation")
    users_cleaned = clean_users_task(users_raw)
    posts_cleaned = clean_posts_task(posts_raw)
    posts_enriched = enrich_posts_task(posts_cleaned, users_cleaned)
    
    # ========== STAGE 3: ANALYTICS ==========
    logger.info("\n📊 STAGE 3: Analytics & Statistics")
    user_stats = user_activity_task(posts_cleaned, users_cleaned)
    top_authors = top_authors_task(user_stats)
    data_summary = summary_task(users_cleaned, posts_cleaned, posts_enriched)
    
    # ========== STAGE 4: EXPORTS ==========
    logger.info("\n💾 STAGE 4: Data Export")
    users_file = export_users_task(users_cleaned)
    posts_file = export_posts_task(posts_enriched)
    stats_file = export_user_stats_task(user_stats)
    authors_file = export_top_authors_task(top_authors)
    summary_file = export_summary_task(data_summary)
    
    # ========== COMPLETION ==========
    logger.info("\n" + "="*60)
    logger.info("✅ Pipeline Completed Successfully!")
    logger.info("="*60)
    logger.info("\n📁 Generated Files:")
    logger.info(f"  - {users_file}")
    logger.info(f"  - {posts_file}")
    logger.info(f"  - {stats_file}")
    logger.info(f"  - {authors_file}")
    logger.info(f"  - {summary_file}")
    
    return {
        "users_file": users_file,
        "posts_file": posts_file,
        "stats_file": stats_file,
        "authors_file": authors_file,
        "summary_file": summary_file
    }


if __name__ == "__main__":
    # Run the pipeline
    result = modular_data_pipeline()
    print("\n✨ Pipeline execution complete!")
    print(f"📊 Results: {result}")
