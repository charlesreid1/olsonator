import os
import json


with open('matched_donch_kenpom.txt', 'r') as f:
    lines = f.readlines()

kp2donch = {}
for line in lines:
    tokens = [j.strip() for j in line.split("|")]
    kp2donch[tokens[1]] = tokens[0]

with open('team_leagues.txt', 'r') as f:
    lines = f.readlines()

final = {}
for line in lines:
    for kp in kp2donch:
        if kp in line:
            tokens = [j.strip() for j in line.split("\t")]
            lea = tokens[-1]
            donch = kp2donch[kp]
            final[donch] = lea

fpath = os.path.abspath(os.path.join('..', 'json', 'leagues.json'))
print(f"Dumping leagues to file: {fpath}")
with open(fpath, 'w') as f:
    json.dump(final, f, indent=4)
