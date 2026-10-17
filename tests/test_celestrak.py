from types import SimpleNamespace

import backend.celestrak as celestrak


def test_get_satellite_data_requests_catalog_number(monkeypatch):
    response = SimpleNamespace(
        raise_for_status=lambda: None,
        json=lambda: [{"NORAD_CAT_ID": "34220", "OBJECT_NAME": "PSLV DEB"}],
    )
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return response

    monkeypatch.setattr(celestrak.requests, "get", fake_get)

    assert celestrak.get_satellite_data(34220) == response.json()
    assert calls[0][0] == celestrak.BASE_URL
    assert calls[0][1]["params"] == {"CATNR": 34220, "FORMAT": "JSON"}
    assert calls[0][1]["timeout"] == 30
