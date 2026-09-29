from datetime import datetime, timezone

from backend.propagator import propagate_satellite

# Test the satellite propagator. Retrieve the satellite info from 
# CelesTrak, propagate to the current time, return its current position and velocity

position, velocity = propagate_satellite(
    25544,
    datetime.now(timezone.utc)
)

print("Position (km):")
print(position)

print("\nVelocity (km/s):")
print(velocity)