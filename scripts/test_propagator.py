from datetime import datetime, timezone, timedelta

from backend.propagator import propagate_satellite, create_satrec
from data.satellite_data import get_satellite_data
from sgp4.conveniences import sat_epoch_datetime

# Test the satellite propagator. Retrieve the satellite info from 
# CelesTrak, propagate to the current time, return its current position and velocity

catalog_number = 25544

satellite = create_satrec(catalog_number)

epoch = sat_epoch_datetime(satellite)

print("ISS Epoch:")
print(epoch)

times = {
    "Epoch": epoch,
    "1 Hour After Epoch": epoch + timedelta(hours=1),
    "6 Hours After Epoch": epoch + timedelta(hours=6),
    "1 Day After Epoch": epoch + timedelta(days=1),
}


for label, when in times.items():
    time, position, velocity = propagate_satellite(
        satellite,
        when
    )

    print(f"\n--- {label} ---")
    print(f"Time: {when}")
    print(f"Position (km): {position}")
    print(f"Velocity (km/s): {velocity}")