from backend.celestrak import get_iss_data, get_satellite_data

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
