# Author: Carson Morris
# September 29, 2026
# Coordinates Conversion Functions
# Convert SGP4 positions from Earth-centered inertial (ECI) coords
# to lat/lon/alt coordinates

from sgp4.api import jday
from math import sin, cos, pi
from datetime import timezone

# Convert TEME (True Equator, Mean Equinox) coordinates to ECEF (Earth-Centered, Earth-Fixed) coordinates
def teme_to_ecef(position_teme, time):
    # Make sure the time has timezone information
    if time.tzinfo is None:
        raise ValueError("Time must contain timezone information")

    # Convert time to UTC
    time = time.astimezone(timezone.utc)

    # Convert datetime to Julian Date
    jd, fr = jday(
        time.year,
        time.month,
        time.day,
        time.hour,
        time.minute,
        time.second + time.microsecond / 1_000_000
    )

    # Combine the Julian Date components
    jd = jd + fr

    # Calculate Julian centuries since J2000.0
    T = (jd - 2451545.0) / 36525.0

    # Calculate Greenwich Mean Sidereal Time in degrees (represents the hour angle of the vernal equinox measured along the celestial equator from the Greenwich Meridian)
    gmst = (
        280.46061837
        + 360.98564736629 * (jd - 2451545.0)
        + 0.000387933 * T**2
        - T**3 / 38710000.0
    )

    # Normalize GMST to 0-360 degrees
    gmst = gmst % 360.0

    # Convert GMST from degrees to radians
    theta = gmst * pi / 180.0

    # Extract TEME position
    x_teme, y_teme, z_teme = position_teme

    # Rotate TEME coordinates into ECEF
    x_ecef = x_teme * cos(theta) + y_teme * sin(theta)
    y_ecef = -x_teme * sin(theta) + y_teme * cos(theta)
    z_ecef = z_teme

    return x_ecef, y_ecef, z_ecef

# Convert ECEF coordinates to geodetic (latitude, longitude, altitude)
def ecef_to_geodetic(position_ecef):
    # Placeholder for geodetic conversion logic
    pass