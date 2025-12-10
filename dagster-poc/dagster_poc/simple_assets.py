"""Dagster asset definitions - Modern approach using @asset decorator."""
import requests
import pandas as pd
from dagster import asset, AssetExecutionContext
from typing import Dict
import os


@asset(description="Raw user data fetched from JSONPlaceholder API")
def raw_user_data(context: AssetExecutionContext) -> Dict:
    """
    Fetch data from a public API (JSONPlaceholder).
    Returns raw JSON data.
    """
    url = "https://jsonplaceholder.typicode.com/users"
    context.log.info(f"Fetching data from {url}")
    
    response = requests.get(url)
    response.raise_for_status()
    
    data = response.json()
    context.log.info(f"Successfully fetched {len(data)} records")
    
    return {"data": data, "source": url}


@asset(description="Transformed user data as DataFrame")
def transformed_user_data(context: AssetExecutionContext, raw_user_data: Dict) -> pd.DataFrame:
    """
    Transform raw JSON data into a structured DataFrame.
    Extracts key user information.
    """
    context.log.info("Transforming data...")
    
    users = raw_user_data["data"]
    transformed = []
    
    for user in users:
        transformed.append({
            "id": user["id"],
            "name": user["name"],
            "username": user["username"],
            "email": user["email"],
            "city": user["address"]["city"],
            "company": user["company"]["name"]
        })
    
    df = pd.DataFrame(transformed)
    context.log.info(f"Transformed {len(df)} records")
    
    return df


@asset(description="User data saved to CSV file")
def user_data_csv(context: AssetExecutionContext, transformed_user_data: pd.DataFrame) -> str:
    """
    Save DataFrame to CSV file.
    Returns the file path.
    """
    output_path = "output/dagster_users.csv"
    context.log.info(f"Saving data to {output_path}")
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    transformed_user_data.to_csv(output_path, index=False)
    context.log.info(f"Successfully saved {len(transformed_user_data)} records to {output_path}")
    
    return output_path


@asset(description="Summary statistics of the data extraction")
def data_extraction_summary(
    context: AssetExecutionContext, 
    transformed_user_data: pd.DataFrame, 
    user_data_csv: str
) -> Dict:
    """
    Generate and log a summary of the extraction.
    """
    summary = {
        "total_records": len(transformed_user_data),
        "columns": list(transformed_user_data.columns),
        "output_file": user_data_csv
    }
    
    context.log.info("="*50)
    context.log.info("DATA EXTRACTION SUMMARY")
    context.log.info("="*50)
    context.log.info(f"Total Records: {summary['total_records']}")
    context.log.info(f"Columns: {', '.join(summary['columns'])}")
    context.log.info(f"Output File: {summary['output_file']}")
    context.log.info("="*50)
    
    return summary
