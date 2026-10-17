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
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS satellite_catalog (
                    catalog_number INTEGER PRIMARY KEY,
                    object_name TEXT NOT NULL,
                    object_type TEXT NOT NULL DEFAULT '',
                    data_status_code TEXT NOT NULL DEFAULT '',
                    ops_status_code TEXT NOT NULL DEFAULT '',
                    decay_date TEXT NOT NULL DEFAULT '',
                    orbit_center TEXT NOT NULL DEFAULT '',
                    orbit_type TEXT NOT NULL DEFAULT ''
                )
                """
            )
            catalog_columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(satellite_catalog)")
            }
            for column in (
                "object_type",
                "data_status_code",
                "ops_status_code",
                "decay_date",
                "orbit_center",
                "orbit_type",
            ):
                if column not in catalog_columns:
                    connection.execute(
                        f"ALTER TABLE satellite_catalog "
                        f"ADD COLUMN {column} TEXT NOT NULL DEFAULT ''"
                    )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS satellite_catalog_elements_idx
                ON satellite_catalog (
                    data_status_code,
                    decay_date,
                    orbit_center,
                    orbit_type,
                    object_type
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


def _has_matching_gp_record(data, catalog_number):
    """Confirm a non-empty GP response belongs to the requested catalog number."""
    return (
        isinstance(data, list)
        and bool(data)
        and isinstance(data[0], dict)
        and str(data[0].get("NORAD_CAT_ID", "")) == str(catalog_number)
    )


def get_satellite_data(catalog_number):
    """Validate a NORAD number, then return its current matching GP record."""
    catalog_record = get_catalog_record(catalog_number)
    if catalog_record is None:
        raise ValueError(
            f"NORAD catalog number {catalog_number} is not in the local satellite catalog."
        )
    if catalog_record["decay_date"]:
        raise ValueError(
            f"{catalog_record['object_name']} ({catalog_number}) is marked as decayed "
            f"in SATCAT on {catalog_record['decay_date']} and cannot be tracked."
        )
    if catalog_record["orbit_center"] != "EA":
        raise ValueError(
            f"{catalog_record['object_name']} ({catalog_number}) is not in an Earth-centered orbit."
        )
    if catalog_record["orbit_type"] != "ORB":
        raise ValueError(
            f"{catalog_record['object_name']} ({catalog_number}) does not have an Earth orbit."
        )
    if catalog_record["data_status_code"]:
        raise ValueError(
            f"{catalog_record['object_name']} ({catalog_number}) has SATCAT data status "
            f"'{catalog_record['data_status_code']}' and is not marked as having usable "
            "orbital elements."
        )

    if data_is_current(catalog_number):
        cached_data = load_cached_data(catalog_number)
        if _has_matching_gp_record(cached_data, catalog_number):
            return cached_data

    # A missing or expired record is refreshed from CelesTrak before returning.
    data = fetch_satellite_data(catalog_number)
    if not _has_matching_gp_record(data, catalog_number):
        if data == []:
            with closing(_connect()) as connection:
                with connection:
                    connection.execute(
                        "DELETE FROM satellites WHERE catalog_number = ?",
                        (int(catalog_number),),
                    )
        raise ValueError(
            f"CelesTrak returned no matching GP orbital record for NORAD "
            f"catalog number {catalog_number}."
        )
    save_cached_data(catalog_number, data)
    return data


def is_catalog_number_known(catalog_number):
    """Check whether a number exists in the local SATCAT catalog."""
    return get_catalog_record(catalog_number) is not None


def get_catalog_record(catalog_number):
    """Return local SATCAT metadata for a valid NORAD catalog number."""
    catalog_number = int(catalog_number)
    if catalog_number <= 0 or catalog_number > 999_999_999:
        return None

    _initialize_database()
    with closing(_connect()) as connection:
        row = connection.execute(
            """
            SELECT
                catalog_number,
                object_name,
                object_type,
                decay_date,
                orbit_center,
                data_status_code,
                orbit_type
            FROM satellite_catalog
            WHERE catalog_number = ?
            """,
            (catalog_number,),
        ).fetchone()
    if row is None:
        return None

    return {
        "catalog_number": row[0],
        "object_name": row[1],
        "object_type": row[2],
        "decay_date": row[3],
        "orbit_center": row[4],
        "data_status_code": row[5],
        "orbit_type": row[6],
    }


def load_satellite_catalog():
    """Return eligible objects with a confirmed, cached CelesTrak GP record."""
    _initialize_database()
    with closing(_connect()) as connection:
        catalog_count = connection.execute(
            "SELECT COUNT(*) FROM satellite_catalog"
        ).fetchone()[0]
        if catalog_count == 0:
            raise RuntimeError(
                "The local satellite catalog is empty. A pre-populated "
                "satellites.db is required."
            )
        rows = connection.execute(
            """
            SELECT
                catalog.catalog_number,
                catalog.object_name,
                catalog.object_type,
                orbital_data.data_json
            FROM satellite_catalog AS catalog
            JOIN satellites AS orbital_data
                ON orbital_data.catalog_number = catalog.catalog_number
            WHERE catalog.decay_date = ''
                AND catalog.orbit_center = 'EA'
                AND catalog.orbit_type = 'ORB'
                AND catalog.data_status_code = ''
                AND orbital_data.data_json != '[]'
            ORDER BY catalog.object_name COLLATE NOCASE, catalog.catalog_number
            """
        ).fetchall()

    catalog = []
    for catalog_number, object_name, object_type, data_json in rows:
        orbital_records = json.loads(data_json)
        if not _has_matching_gp_record(orbital_records, catalog_number):
            continue
        catalog.append(
            {
                "catalog_number": catalog_number,
                "object_name": object_name,
                "object_type": object_type,
            }
        )
    return catalog


def get_satellite_catalog():
    """Return trackable objects from the pre-populated local database."""
    return load_satellite_catalog()
