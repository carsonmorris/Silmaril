# Author: Carson Morris
# Silmaril - Created: September 28, 2026
# Satellite Data Manager. Handles local caching and retrieving satellite data.
# Prevents having to fetch data from Celestrak on every request.

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from backend.celestrak import get_satellite_data as fetch_satellite_data


CACHE_DIR = Path("data/satellites")
MAX_DATA_AGE = timedelta(hours=3)


def load_cached_data(catalog_number):
    cache_file = CACHE_DIR / f"{catalog_number}.json"

    with open(cache_file, "r") as file:
        return json.load(file)


def save_cached_data(catalog_number, data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_file = CACHE_DIR / f"{catalog_number}.json"

    with open(cache_file, "w") as file:
        json.dump(data, file, indent=2)


def data_is_current(catalog_number):
    cache_file = CACHE_DIR / f"{catalog_number}.json"

    if not cache_file.exists():
        return False

    modified_time = datetime.fromtimestamp(
        cache_file.stat().st_mtime,
        tz=timezone.utc
    )

    age = datetime.now(timezone.utc) - modified_time

    return age < MAX_DATA_AGE


def get_satellite_data(catalog_number):
    if data_is_current(catalog_number):
        return load_cached_data(catalog_number)

    data = fetch_satellite_data(catalog_number)

    save_cached_data(catalog_number, data)

    return data
