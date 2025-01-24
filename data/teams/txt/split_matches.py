import os
import json


# donchess <--> sagarin

with open('matched_donch_sag.txt', 'r') as f:
    lines = f.readlines()

donch2sag_map = {}
sag2donch_map = {}
for line in lines:
    tokens = [j.strip() for j in line.split("|")]
    donch2sag_map[tokens[0]] = tokens[1]
    sag2donch_map[tokens[1]] = tokens[0]

fpath = os.path.abspath(os.path.join('..', 'json', 'donch2sag.json'))
print(f"Dumping donch2sag mapping to file: {fpath}")
with open(fpath, 'w') as f:
    json.dump(donch2sag_map, f, indent=4)

fpath = os.path.abspath(os.path.join('..', 'json', 'sag2donch.json'))
print(f"Dumping sag2donch mapping to file: {fpath}")
with open(fpath, 'w') as f:
    json.dump(sag2donch_map, f, indent=4)


# donchess <--> kenpom

with open('matched_donch_kenpom.txt', 'r') as f:
    lines = f.readlines()

donch2kenpom_map = {}
kenpom2donch_map = {}
for line in lines:
    tokens = [j.strip() for j in line.split("|")]
    donch2kenpom_map[tokens[0]] = tokens[1]
    kenpom2donch_map[tokens[1]] = tokens[0]

fpath = os.path.abspath(os.path.join('..', 'json', 'donch2kenpom.json'))
print(f"Dumping donch2kenpom mapping to file: {fpath}")
with open(fpath, 'w') as f:
    json.dump(donch2kenpom_map, f, indent=4)

fpath = os.path.abspath(os.path.join('..', 'json', 'kenpom2donch.json'))
print(f"Dumping kenpom2donch mapping to file: {fpath}")
with open(fpath, 'w') as f:
    json.dump(kenpom2donch_map, f, indent=4)


# donchess <--> teamrankings

with open('matched_donch_teamrankings.txt', 'r') as f:
    lines = f.readlines()

donch2teamrankings_map = {}
teamrankings2donch_map = {}
for line in lines:
    tokens = [j.strip() for j in line.split("|")]
    donch2teamrankings_map[tokens[0]] = tokens[1]
    teamrankings2donch_map[tokens[1]] = tokens[0]

fpath = os.path.abspath(os.path.join('..', 'json', 'donch2teamrankings.json'))
print(f"Dumping donch2teamrankings mapping to file: {fpath}")
with open(fpath, 'w') as f:
    json.dump(donch2teamrankings_map, f, indent=4)

fpath = os.path.abspath(os.path.join('..', 'json', 'teamrankings2donch.json'))
print(f"Dumping teamrankings2donch mapping to file: {fpath}")
with open(fpath, 'w') as f:
    json.dump(teamrankings2donch_map, f, indent=4)

