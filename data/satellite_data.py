# Author: Carson Morris
# Silmaril - Created at: September 28, 2026
# Description: Manage the local SQLite cache of satellite orbital data.
# Avoid fetching data from CelesTrak on every request.

from contextlib import closing
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sqlite3

from backend.celestrak import get_satellite_data as fetch_satellite_data


# Keep the database beside this module so its location does not depend on the
# directory from which the application is launched.
DATABASE_PATH = Path(__file__).resolve().with_name("satellites.db")
MAX_DATA_AGE = timedelta(hours=3)


def _connect():
    """Open the cache database, creating its parent directory if needed."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DATABASE_PATH, timeout=30)


def _initialize_database():
    """Create the satellite cache table if this is a fresh database."""
    with closing(_connect()) as connection:
        with connection:
            connection.execute(
                """
                -- Preserve the source OMM payload and when it entered the cache.
                CREATE TABLE IF NOT EXISTS satellites (
                    catalog_number INTEGER PRIMARY KEY,
                    data_json TEXT NOT NULL,
                    cached_at REAL NOT NULL
                )
                """
            )


def load_cached_data(catalog_number):
    """Return the cached OMM record for a catalog number."""
    _initialize_database()
    with closing(_connect()) as connection:
        row = connection.execute(
            "SELECT data_json FROM satellites WHERE catalog_number = ?",
            (int(catalog_number),),
        ).fetchone()

    if row is None:
        raise FileNotFoundError(
            f"No cached satellite data found for catalog number {catalog_number}"
        )

    return json.loads(row[0])


def save_cached_data(catalog_number, data):
    """Insert or replace a record and reset its cache age to the current UTC time."""
    _initialize_database()
    with closing(_connect()) as connection:
        with connection:
            connection.execute(
                """
                -- Replace stale records in place so each catalog number stays unique.
                INSERT INTO satellites (catalog_number, data_json, cached_at)
                VALUES (?, ?, ?)
                ON CONFLICT(catalog_number) DO UPDATE SET
                    data_json = excluded.data_json,
                    cached_at = excluded.cached_at
                """,
                (
                    int(catalog_number),
                    json.dumps(data),
                    datetime.now(timezone.utc).timestamp(),
                ),
            )


def data_is_current(catalog_number):
    """Check whether the record exists and is younger than the cache limit."""
    _initialize_database()
    with closing(_connect()) as connection:
        row = connection.execute(
            "SELECT cached_at FROM satellites WHERE catalog_number = ?",
            (int(catalog_number),),
        ).fetchone()

    if row is None:
        return False

    cached_at = datetime.fromtimestamp(row[0], tz=timezone.utc)
    age = datetime.now(timezone.utc) - cached_at
    return age < MAX_DATA_AGE


def get_satellite_data(catalog_number):
    if data_is_current(catalog_number):
        return load_cached_data(catalog_number)

    # A missing or expired record is refreshed from CelesTrak before returning.
    data = fetch_satellite_data(catalog_number)
    save_cached_data(catalog_number, data)
    return data
