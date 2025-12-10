"""Data extraction operations for Dagster POC."""
import json
import requests
import pandas as pd
from dagster import op, Out, Output
from typing import Dict, List


@op(out=Out(Dict))
def fetch_data_from_api(context) -> Dict:
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


@op
def transform_data(context, raw_data: Dict) -> pd.DataFrame:
    """
    Transform raw JSON data into a structured DataFrame.
    Extracts key user information.
    """
    context.log.info("Transforming data...")
    
    users = raw_data["data"]
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


@op
def save_to_csv(context, dataframe: pd.DataFrame) -> str:
    """
    Save DataFrame to CSV file.
    Returns the file path.
    """
    output_path = "output/dagster_users.csv"
    context.log.info(f"Saving data to {output_path}")
    
    # Create output directory if it doesn't exist
    import os
    os.makedirs("output", exist_ok=True)
    
    dataframe.to_csv(output_path, index=False)
    context.log.info(f"Successfully saved {len(dataframe)} records to {output_path}")
    
    return output_path


@op
def generate_summary(context, dataframe: pd.DataFrame, file_path: str):
    """
    Generate and log a summary of the extraction.
    """
    summary = {
        "total_records": len(dataframe),
        "columns": list(dataframe.columns),
        "output_file": file_path
    }
    
    context.log.info("="*50)
    context.log.info("DATA EXTRACTION SUMMARY")
    context.log.info("="*50)
    context.log.info(f"Total Records: {summary['total_records']}")
    context.log.info(f"Columns: {', '.join(summary['columns'])}")
    context.log.info(f"Output File: {summary['output_file']}")
    context.log.info("="*50)
    
    return summary
