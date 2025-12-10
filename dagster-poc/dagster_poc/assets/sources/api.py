"""Source assets - Data extraction from external sources."""
import requests
from dagster import asset, AssetExecutionContext
from typing import Dict


@asset(
    group_name="sources",
    description="Raw user data fetched from JSONPlaceholder API",
    compute_kind="api"
)
def api_users_raw(context: AssetExecutionContext) -> Dict:
    """
    Fetch user data from JSONPlaceholder API.
    
    Returns:
        Dict containing raw user data and metadata
    """
    url = "https://jsonplaceholder.typicode.com/users"
    context.log.info(f"Fetching user data from {url}")
    
    response = requests.get(url)
    response.raise_for_status()
    
    data = response.json()
    context.log.info(f"Successfully fetched {len(data)} user records")
    
    return {
        "data": data,
        "source": url,
        "record_count": len(data)
    }


@asset(
    group_name="sources",
    description="Raw posts data fetched from JSONPlaceholder API",
    compute_kind="api"
)
def api_posts_raw(context: AssetExecutionContext) -> Dict:
    """
    Fetch posts data from JSONPlaceholder API.
    
    Returns:
        Dict containing raw posts data and metadata
    """
    url = "https://jsonplaceholder.typicode.com/posts"
    context.log.info(f"Fetching posts data from {url}")
    
    response = requests.get(url)
    response.raise_for_status()
    
    data = response.json()
    context.log.info(f"Successfully fetched {len(data)} post records")
    
    return {
        "data": data,
        "source": url,
        "record_count": len(data)
    }
