# Author: Carson Morris
# Silmaril - Created: September 28, 2026
# Celestrak Data Fetcher. Retrieve orbital data for satellites from Celestrak.

import requests

# For testing purposes, get specifically the ISS data
def get_iss_data():
    # Use Celestrak's query format to retrieve ISS data
    url = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=JSON"
    response = requests.get(url)
    # Convert to JSON
    data = response.json()
    return data

# General function to retrieve data for any satellite
def get_satellite_data(catalog_number):
    url = (
        f"https://celestrak.org/NORAD/elements/gp.php"
        f"?CATNR={catalog_number}&FORMAT=JSON"
    )

    response = requests.get(url)
    response.raise_for_status()

    return response.json()