# Author: Carson Morris
# Silmaril - Created at: September 28, 2026
# Description: Fetch orbital data for satellites from CelesTrak.

import requests


BASE_URL = "https://celestrak.org/NORAD/elements/gp.php"

HEADERS = {
    "User-Agent": "Silmaril/0.1"
}

def get_satellite_data(catalog_number):
    """Fetch a satellite's GP JSON record by NORAD number or raise on HTTP errors."""
    params = {
        "CATNR": catalog_number,
        "FORMAT": "JSON"
    }

    response = requests.get(
        BASE_URL,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.json()
