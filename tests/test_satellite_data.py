# Author: Carson Morris
# Silmaril - Created at: October 17, 2026
# Description: Test SQLite satellite cache reads, writes, and refreshes.

from datetime import timedelta
import sqlite3

import pytest
import data.satellite_data as satellite_data


def use_temporary_database(monkeypatch, tmp_path):
    """Point cache tests at an isolated, pre-populated local catalog database."""
    monkeypatch.setattr(satellite_data, "DATABASE_PATH", tmp_path / "satellites.db")
    satellite_data._initialize_database()
    catalog_records = [
        (25544, "ISS", "PAY", "", "+", "", "EA", "ORB"),
        (12345, "Test satellite", "PAY", "", "+", "", "EA", "ORB"),
        (12346, "No elements satellite", "PAY", "NEA", "+", "", "EA", "ORB"),
        (12347, "No orbit type", "PAY", "", "+", "", "EA", ""),
        (34220, "PSLV DEB", "DEB", "", "D", "2023-04-21", "EA", "IMP"),
        (50032, "TEST DEB", "DEB", "", "", "", "EA", "ORB"),
    ]
    with sqlite3.connect(satellite_data.DATABASE_PATH) as connection:
        connection.executemany(
            """
            INSERT INTO satellite_catalog (
                catalog_number,
                object_name,
                object_type,
                data_status_code,
                ops_status_code,
                decay_date,
                orbit_center,
                orbit_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            catalog_records,
        )


def test_save_and_load_cached_data(monkeypatch, tmp_path):
    use_temporary_database(monkeypatch, tmp_path)
    data = [{"NORAD_CAT_ID": 12345, "OBJECT_NAME": "Test satellite"}]

    satellite_data.save_cached_data(12345, data)

    assert satellite_data.load_cached_data(12345) == data
    assert satellite_data.data_is_current(12345)


def test_empty_database_requires_prepopulated_catalog(monkeypatch, tmp_path):
    monkeypatch.setattr(satellite_data, "DATABASE_PATH", tmp_path / "satellites.db")

    with pytest.raises(RuntimeError, match="pre-populated satellites.db is required"):
        satellite_data.get_satellite_catalog()


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


def test_cached_orbital_records_include_satcat_object_types(monkeypatch, tmp_path):
    use_temporary_database(monkeypatch, tmp_path)
    iss_data = [{"NORAD_CAT_ID": "25544", "OBJECT_NAME": "ISS"}]
    satellite_data.save_cached_data(25544, iss_data)
    debris_data = [{"NORAD_CAT_ID": "50032", "OBJECT_NAME": "TEST DEB"}]
    satellite_data.save_cached_data(50032, debris_data)
    monkeypatch.setattr(
        satellite_data,
        "fetch_satellite_data",
        lambda _catalog_number: pytest.fail("fresh cached records must not fetch"),
    )

    catalog = satellite_data.get_satellite_catalog()

    assert catalog == [
        {"catalog_number": 25544, "object_name": "ISS", "object_type": "PAY"},
        {"catalog_number": 50032, "object_name": "TEST DEB", "object_type": "DEB"},
    ]
    assert all(entry["catalog_number"] != 12345 for entry in catalog)
    assert satellite_data.get_satellite_catalog() == catalog
    assert satellite_data.load_cached_data(25544) == iss_data
    with sqlite3.connect(satellite_data.DATABASE_PATH) as connection:
        assert connection.execute(
            "SELECT 1 FROM satellites WHERE catalog_number = 50032"
        ).fetchone() is not None


def test_empty_gp_response_is_not_cached_or_listed(monkeypatch, tmp_path):
    use_temporary_database(monkeypatch, tmp_path)
    satellite_data.save_cached_data(
        12345, [{"NORAD_CAT_ID": "12345", "OBJECT_NAME": "Test satellite"}]
    )
    monkeypatch.setattr(satellite_data, "MAX_DATA_AGE", timedelta(seconds=-1))
    monkeypatch.setattr(satellite_data, "fetch_satellite_data", lambda _number: [])

    with pytest.raises(ValueError, match="no matching GP orbital record"):
        satellite_data.get_satellite_data(12345)

    with sqlite3.connect(satellite_data.DATABASE_PATH) as connection:
        assert connection.execute(
            "SELECT 1 FROM satellites WHERE catalog_number = 12345"
        ).fetchone() is None
    assert all(
        entry["catalog_number"] != 12345
        for entry in satellite_data.get_satellite_catalog()
    )


def test_local_catalog_validates_custom_numbers_without_network(
    monkeypatch, tmp_path
):
    use_temporary_database(monkeypatch, tmp_path)

    def unexpected_request(*_args, **_kwargs):
        pytest.fail("unknown catalog number must be rejected before network access")

    monkeypatch.setattr(satellite_data, "fetch_satellite_data", unexpected_request)

    assert satellite_data.is_catalog_number_known(34220)
    assert not satellite_data.is_catalog_number_known(999_999_999)
    with pytest.raises(ValueError, match="not in the local"):
        satellite_data.get_satellite_data(999_999_999)
    with pytest.raises(ValueError, match="marked as decayed"):
        satellite_data.get_satellite_data(34220)
    with pytest.raises(ValueError, match="SATCAT data status 'NEA'"):
        satellite_data.get_satellite_data(12346)
    with pytest.raises(ValueError, match="does not have an Earth orbit"):
        satellite_data.get_satellite_data(12347)

    with sqlite3.connect(satellite_data.DATABASE_PATH) as connection:
        record = connection.execute(
            """
            SELECT object_name, object_type, decay_date, orbit_type
            FROM satellite_catalog WHERE catalog_number = 34220
            """
        ).fetchone()
    assert record == ("PSLV DEB", "DEB", "2023-04-21", "IMP")


def test_cached_catalog_and_fresh_iss_do_not_contact_celestrak(
    monkeypatch, tmp_path
):
    use_temporary_database(monkeypatch, tmp_path)
    iss_data = [{"NORAD_CAT_ID": 25544, "OBJECT_NAME": "ISS"}]
    satellite_data.save_cached_data(25544, iss_data)
    satellite_data.save_cached_data(
        50032, [{"NORAD_CAT_ID": 50032, "OBJECT_NAME": "TEST DEB"}]
    )
    def unexpected_request(*_args, **_kwargs):
        raise AssertionError("CelesTrak should not be contacted for cached ISS data")

    monkeypatch.setattr(satellite_data, "fetch_satellite_data", unexpected_request)

    catalog = satellite_data.get_satellite_catalog()
    assert catalog[0] == {
        "catalog_number": 25544,
        "object_name": "ISS",
        "object_type": "PAY",
    }
    assert any(
        entry["catalog_number"] == 50032 and entry["object_type"] == "DEB"
        for entry in catalog
    )
    assert satellite_data.get_satellite_data(25544) == iss_data


def test_satellite_catalog_reads_prepopulated_database(monkeypatch, tmp_path):
    use_temporary_database(monkeypatch, tmp_path)
    iss_data = [{"NORAD_CAT_ID": 25544, "OBJECT_NAME": "ISS"}]
    satellite_data.save_cached_data(25544, iss_data)

    catalog = satellite_data.get_satellite_catalog()

    assert catalog == [
        {"catalog_number": 25544, "object_name": "ISS", "object_type": "PAY"}
    ]
    assert satellite_data.is_catalog_number_known(12345)
    assert satellite_data.get_satellite_data(25544) == iss_data


def test_satcat_debris_requires_a_cached_gp_record(monkeypatch, tmp_path):
    use_temporary_database(monkeypatch, tmp_path)

    assert satellite_data.is_catalog_number_known(34220)
    with sqlite3.connect(satellite_data.DATABASE_PATH) as connection:
        record = connection.execute(
            """
            SELECT object_name, object_type, decay_date
            FROM satellite_catalog WHERE catalog_number = 34220
            """
        ).fetchone()
        registry_count = connection.execute(
            "SELECT COUNT(*) FROM satellite_catalog"
        ).fetchone()[0]

    assert record == ("PSLV DEB", "DEB", "2023-04-21")
    assert registry_count == 6
    assert not satellite_data.is_catalog_number_known(999_999_999)

    satellite_data.save_cached_data(
        50032, [{"NORAD_CAT_ID": 50032, "OBJECT_NAME": "TEST DEB"}]
    )
    satellite_data.save_cached_data(25544, [{"NORAD_CAT_ID": 25544}])
    catalog = satellite_data.get_satellite_catalog()
    debris_count = sum(
        satellite["object_type"] == "DEB" for satellite in catalog
    )
    assert debris_count == 1
    assert all(satellite["catalog_number"] != 34220 for satellite in catalog)
    assert all(satellite["catalog_number"] != 12346 for satellite in catalog)
    assert all(satellite["catalog_number"] != 12345 for satellite in catalog)
