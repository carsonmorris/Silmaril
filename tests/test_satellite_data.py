# Author: Carson Morris
# Silmaril - Created at: October 17, 2026
# Description: Test SQLite satellite cache reads, writes, and refreshes.

from datetime import datetime, timedelta, timezone

import data.satellite_data as satellite_data


def use_temporary_database(monkeypatch, tmp_path):
    monkeypatch.setattr(satellite_data, "DATABASE_PATH", tmp_path / "satellites.db")


def test_save_and_load_cached_data(monkeypatch, tmp_path):
    use_temporary_database(monkeypatch, tmp_path)
    data = [{"NORAD_CAT_ID": 12345, "OBJECT_NAME": "Test satellite"}]

    satellite_data.save_cached_data(12345, data)

    assert satellite_data.load_cached_data(12345) == data
    assert satellite_data.data_is_current(12345)


def test_get_satellite_data_refreshes_stale_record(monkeypatch, tmp_path):
    use_temporary_database(monkeypatch, tmp_path)
    old_data = [{"NORAD_CAT_ID": 12345, "OBJECT_NAME": "Old name"}]
    fresh_data = [{"NORAD_CAT_ID": 12345, "OBJECT_NAME": "New name"}]
    satellite_data.save_cached_data(12345, old_data)
    monkeypatch.setattr(satellite_data, "MAX_DATA_AGE", timedelta(seconds=-1))
    monkeypatch.setattr(
        satellite_data, "fetch_satellite_data", lambda _catalog_number: fresh_data
    )

    assert satellite_data.get_satellite_data(12345) == fresh_data
    assert satellite_data.load_cached_data(12345) == fresh_data
