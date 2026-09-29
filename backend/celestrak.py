# Author: Carson Morris
# Silmaril - Created: September 28, 2026
# Celestrak Data Fetcher. Retrieve orbital data for satellites from Celestrak.

import requests

# For testing purposes, get specifically the ISS data
def get_iss_data():
    url = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=JSON"
    response = requests.get(url)
    data = response.json()
    return data