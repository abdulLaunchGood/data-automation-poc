from dagster import Definitions
from .jobs import data_extraction_job
# Import simple assets from simple_assets.py
from .simple_assets import (
    raw_user_data,
    transformed_user_data,
    user_data_csv,
    data_extraction_summary
)
# Import modular assets from assets/ package
from .assets import ALL_ASSETS as MODULAR_ASSETS
# Import schedules for assets
from .schedules import ALL_SCHEDULES

# Combine simple and modular assets
all_assets = [
    # Simple assets (original POC - from simple_assets.py)
    raw_user_data,
    transformed_user_data,
    user_data_csv,
    data_extraction_summary,
] + MODULAR_ASSETS  # Modular assets (from assets/ package)

defs = Definitions(
    assets=all_assets,
    jobs=[data_extraction_job],
    schedules=ALL_SCHEDULES,  # Asset schedules!
)
