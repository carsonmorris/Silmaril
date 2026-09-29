from backend.celestrak import get_iss_data

data = get_iss_data()

print("Confirm returned JSON is a list of len 1, containing dictionary JSON values:")
print(type(data))
print(len(data))
print(type(data[0]))

iss = data[0]

print("ISS Data:")
for key, value in iss.items():
    print(f"  {key}: {value}")