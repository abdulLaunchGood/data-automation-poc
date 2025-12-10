"""Data extraction tasks for Prefect POC."""
import requests
import pandas as pd
from prefect import task
from typing import Dict, List
import os


@task(name="Fetch Data from API", retries=3, retry_delay_seconds=5)
def fetch_data_from_api() -> Dict:
    """
    Fetch data from a public API (JSONPlaceholder).
    Returns raw JSON data.
    """
    url = "https://jsonplaceholder.typicode.com/users"
    print(f"Fetching data from {url}")
    
    response = requests.get(url)
    response.raise_for_status()
    
    data = response.json()
    print(f"Successfully fetched {len(data)} records")
    
    return {"data": data, "source": url}


@task(name="Transform Data")
def transform_data(raw_data: Dict) -> pd.DataFrame:
    """
    Transform raw JSON data into a structured DataFrame.
    Extracts key user information.
    """
    print("Transforming data...")
    
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
    print(f"Transformed {len(df)} records")
    
    return df


@task(name="Save to CSV")
def save_to_csv(dataframe: pd.DataFrame) -> str:
    """
    Save DataFrame to CSV file.
    Returns the file path.
    """
    output_path = "output/prefect_users.csv"
    print(f"Saving data to {output_path}")
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    dataframe.to_csv(output_path, index=False)
    print(f"Successfully saved {len(dataframe)} records to {output_path}")
    
    return output_path


@task(name="Generate Summary")
def generate_summary(dataframe: pd.DataFrame, file_path: str) -> Dict:
    """
    Generate and log a summary of the extraction.
    """
    summary = {
        "total_records": len(dataframe),
        "columns": list(dataframe.columns),
        "output_file": file_path
    }
    
    print("=" * 50)
    print("DATA EXTRACTION SUMMARY")
    print("=" * 50)
    print(f"Total Records: {summary['total_records']}")
    print(f"Columns: {', '.join(summary['columns'])}")
    print(f"Output File: {summary['output_file']}")
    print("=" * 50)
    
    return summary
