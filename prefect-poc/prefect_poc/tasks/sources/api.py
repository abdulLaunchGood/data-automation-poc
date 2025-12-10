"""API data extraction tasks."""
import requests
from prefect import task
from prefect.logging import get_run_logger


@task(name="fetch_users", tags=["api", "sources"], retries=3, retry_delay_seconds=5)
def fetch_users_task():
    """Fetch users from JSONPlaceholder API."""
    logger = get_run_logger()
    
    url = "https://jsonplaceholder.typicode.com/users"
    logger.info(f"Fetching users from {url}")
    
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    logger.info(f"Successfully fetched {len(data)} users")
    
    return {"data": data}


@task(name="fetch_posts", tags=["api", "sources"], retries=3, retry_delay_seconds=5)
def fetch_posts_task():
    """Fetch posts from JSONPlaceholder API."""
    logger = get_run_logger()
    
    url = "https://jsonplaceholder.typicode.com/posts"
    logger.info(f"Fetching posts from {url}")
    
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    logger.info(f"Successfully fetched {len(data)} posts")
    
    return {"data": data}
