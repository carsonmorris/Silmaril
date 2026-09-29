from data.satellite_data import get_satellite_data
from backend.models import OrbitalElements, OrbitalMetadata


# Request the ISS data. Either from the Cache (if its new) or from Celestrak.
data = get_satellite_data(25544)
iss = data[0]

print("International Space Station Data:")
for key, value in iss.items():
    print(f"  {key}: {value}")


# Test OrbitalElements model
orbital_elements = OrbitalElements(**iss)

print("\nTest Orbital Elements Class:")
print(f"Epoch: {orbital_elements.epoch}")
print(f"Mean Motion: {orbital_elements.mean_motion}")
print(f"Eccentricity: {orbital_elements.eccentricity}")
print(f"Inclination: {orbital_elements.inclination}")
print(f"RAAN: {orbital_elements.ra_of_asc_node}")
print(f"Argument of Pericenter: {orbital_elements.arg_of_pericenter}")
print(f"Mean Anomaly: {orbital_elements.mean_anomaly}")
print(f"BSTAR: {orbital_elements.bstar}")


# Test OrbitalMetadata model
orbital_metadata = OrbitalMetadata(**iss)

print("\nTest Orbital Metadata Class:")
print(f"Object Name: {orbital_metadata.object_name}")
print(f"Object ID: {orbital_metadata.object_id}")
print(f"NORAD Catalog ID: {orbital_metadata.norad_cat_id}")
print(f"Ephemeris Type: {orbital_metadata.ephemeris_type}")
print(f"Classification Type: {orbital_metadata.classification_type}")
print(f"Element Set Number: {orbital_metadata.element_set_no}")
