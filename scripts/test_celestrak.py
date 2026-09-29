from backend.celestrak import get_iss_data, get_satellite_data
from backend.models import OrbitalElements

data = get_iss_data()
iss = data[0]

print("ISS Data:")
for key, value in iss.items():
    print(f"  {key}: {value}")

print("\n")

# Test the general satellite data function
data2 = get_satellite_data(25544)
geniss = data2[0]

print("General Satellite Data Function, with ISS Catalog Number 25544:")
for key, value in geniss.items():
    print(f"  {key}: {value}")

# elements = OrbitalElements(
#    object_name=iss["OBJECT_NAME"],
#    norad_cat_id=iss["NORAD_CAT_ID"],
#    epoch=iss["EPOCH"],
#    mean_motion=iss["MEAN_MOTION"],
#    eccentricity=iss["ECCENTRICITY"],
#    inclination=iss["INCLINATION"],
#    ra_of_asc_node=iss["RA_OF_ASC_NODE"],
#    arg_of_pericenter=iss["ARG_OF_PERICENTER"],
#    mean_anomaly=iss["MEAN_ANOMALY"],
#    bstar=iss["BSTAR"]
# )

orbital_elements = OrbitalElements(**data[0])

print("\nTest Orbital Elements Class:")
print(orbital_elements.object_name)
print(orbital_elements.norad_cat_id)
print(orbital_elements.epoch)
print(orbital_elements.inclination)
print(orbital_elements.eccentricity)
print(orbital_elements.mean_motion)

print("Raw Keys:")
print(data[0].keys())
