import os
from geopy import geocoders

gn = geocoders.GeoNames(username=os.environ['GEONAMES_USERNAME'])

print("Loading cities for each school from geo_cities.txt")
with open('geo_cities.txt', 'r') as f:
    lines = f.readlines()

lines = [j.strip() for j in lines if len(j)>0]

print("Requesting lat/long for each city")
cities = {}
latlongs = {}
for line in lines:
    school, city = line.split(" | ")
    cities[school] = city
    print(f"\t{city} in progress")

    loc = gn.geocode(city, exactly_one=True)
    if loc is not None and hasattr(loc, 'latitude') and hasattr(loc, 'longitude'):
        latlongs[school] = (loc.latitude, loc.longitude)
    else:
        print(f"\tXXXXXXXXX {city} not found??")

print("Writing lat/long to geo_latlong.txt")
with open('geo_latlong.txt', 'w') as f:
    for school, latlong in latlongs.items():
        f.write(f"{school} | {latlong[0]} {latlong[1]}\n")

print("Done.")
