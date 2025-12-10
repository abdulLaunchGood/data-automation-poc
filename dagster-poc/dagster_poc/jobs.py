"""Dagster job definitions."""
from dagster import job
from .ops import fetch_data_from_api, transform_data, save_to_csv, generate_summary


@job
def data_extraction_job():
    """
    Data extraction pipeline that:
    1. Fetches data from API
    2. Transforms the data
    3. Saves to CSV
    4. Generates a summary
    """
    raw_data = fetch_data_from_api()
    transformed_df = transform_data(raw_data)
    file_path = save_to_csv(transformed_df)
    generate_summary(transformed_df, file_path)
