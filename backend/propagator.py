# Author: Carson Morris
# Silmaril - Created at: September 28, 2026
# Description: Propagate satellite orbits and calculate positions and velocities.

from sgp4.api import Satrec, SGP4_ERRORS, WGS72, jday  # Satellite record from SGP4
from sgp4 import omm
from datetime import timezone

from data.satellite_data import get_satellite_data

# The current sgp4 library supports initializing a Satrec directly from an OMM record with omm.initialize().
def create_satrec(catalog_number):
    data = get_satellite_data(catalog_number)
    if not data:
        raise ValueError(
            f"No Satellite data found for catalog number {catalog_number}"
        )
    record = data[0]
    satellite = Satrec()  # Create an empty SGP4 satellite record.
    omm.initialize(satellite, record, WGS72)  # Initialize it from the OMM record using WGS72.
    return satellite  # Return the SGP4-compatible orbit representation.



# Propagate a satellite to a specific UTC datetime. Returns: position: (x, y, z) in kilometers velocity: (vx, vy, vz) in kilometers per second at given time, and the time
# Note: SGP4 uses radians instead of degrees
def propagate_satellite(satellite, time): 
    if time.tzinfo is None:
        raise ValueError("Time must contain timezone information")

    time = time.astimezone(timezone.utc)
    
    # jd is the whole-day component; fr is the fractional-day component.
    jd, fr, = jday(  # Convert calendar date and time to Julian date components.
        time.year, 
        time.month, 
        time.day, 
        time.hour, 
        time.minute,
        time.second + time.microsecond/1_000_000)

    error, position, velocity = satellite.sgp4(jd, fr)
    if error != 0:
        raise ValueError(f"Error occurred while propagating satellite: {SGP4_ERRORS[error]}")
    
    # Return position xyz and velocity xyz in terms of TEME: True Equator, Mean Equinox. A Cartesian Earth-centered coordinate
    return position, velocity