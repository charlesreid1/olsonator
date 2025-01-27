import os
import json


# Cities

with open('geo_cities.txt', 'r') as f:
    lines = f.readlines()

geo_cities = {}
for line in lines:
    tokens = [j.strip() for j in line.split("|")]
    team, city = tokens[0], tokens[1]
    geo_cities[team] = city

fname = 'geo_cities.json'
fpath = os.path.abspath(os.path.join('..', 'json', fname))
print(f"Dumping mapping to file: {fpath}")
with open(fpath, 'w') as f:
    json.dump(geo_cities, f, indent=4)


# Lat/long

with open('geo_latlong.txt', 'r') as f:
    lines = f.readlines()

geo_latlong = {}
for line in lines:
    tokens = [j.strip() for j in line.split("|")]
    team, latlong = tokens[0], tokens[1]
    lat, long = latlong.split(" ")
    geo_latlong[team] = (float(lat), float(long))

fname = 'geo_latlong.json'
fpath = os.path.abspath(os.path.join('..', 'json', fname))
print(f"Dumping mapping to file: {fpath}")
with open(fpath, 'w') as f:
    json.dump(geo_latlong, f, indent=4)

