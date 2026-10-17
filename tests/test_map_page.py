from main import create_map_page


def test_map_initial_zoom_is_consistent_across_satellite_paths():
    position = {
        "latitude": 12.0,
        "longitude": 34.0,
        "altitude": 400.0,
        "timestamp": "2026-10-17 12:00:00 UTC",
        "timestamp_unix": 1792243200,
    }
    satellite_data = {}
    paths = [
        [[10.0, 30.0, 1792242600], [12.0, 34.0, 1792243200]],
        [[-60.0, -120.0, 1792242600], [12.0, 34.0, 1792243200]],
    ]

    for path_history in paths:
        page = create_map_page(
            12345,
            "Test satellite",
            position,
            path_history,
            satellite_data,
        )

        assert "liveMap.setView(L.latLngBounds(initialViewPoints).getCenter(), 4);" in page
        assert "liveMap.fitBounds(initialViewPoints" not in page
