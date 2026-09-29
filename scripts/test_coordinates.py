from datetime import datetime, timezone

from backend.propagator import create_satrec, propagate_satellite
from backend.coordinates import teme_to_ecef, ecef_to_geodetic



satellite = create_satrec(25544)

time = datetime.now(tz=timezone.utc)

position_teme, velocity = propagate_satellite(satellite, time)

position_ecef = teme_to_ecef(position_teme, time)

print("TEME:")
print(f"  Position: {position_teme}")

print("\nECEF:")
print(f"  Position: {position_ecef}")

latitude, longitude, altitude = ecef_to_geodetic(position_ecef)

print("\nGeodetic:")
print(f"Latitude:  {latitude:.6f}°")
print(f"Longitude: {longitude:.6f}°")
print(f"Altitude:  {altitude:.3f} km")