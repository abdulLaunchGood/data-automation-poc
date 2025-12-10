"""Prefect flow definitions."""
from prefect import flow
from .tasks import fetch_data_from_api, transform_data, save_to_csv, generate_summary


@flow(name="Data Extraction Flow", log_prints=True)
def data_extraction_flow():
    """
    Data extraction pipeline that:
    1. Fetches data from API
    2. Transforms the data
    3. Saves to CSV
    4. Generates a summary
    """
    # Fetch data from API
    raw_data = fetch_data_from_api()
    
    # Transform data
    transformed_df = transform_data(raw_data)
    
    # Save to CSV
    file_path = save_to_csv(transformed_df)
    
    # Generate summary
    summary = generate_summary(transformed_df, file_path)
    
    return summary


if __name__ == "__main__":
    # Run the flow
    data_extraction_flow()
