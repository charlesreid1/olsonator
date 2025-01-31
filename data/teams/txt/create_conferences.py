import os
import json


with open('matched_donch_kenpom.txt', 'r') as f:
    lines = f.readlines()

kp2donch = {}
for line in lines:
    tokens = [j.strip() for j in line.split("|")]
    kp2donch[tokens[1]] = tokens[0]

with open('team_conferences.txt', 'r') as f:
    lines = f.readlines()

final = {}
for line in lines:
    tokens = [j.strip() for j in line.split("\t")]
    if tokens[0] in kp2donch:
        lea = tokens[1]
        donch = kp2donch[tokens[0]]
        final[donch] = lea

fpath = os.path.abspath(os.path.join('..', 'json', 'team_conferences.json'))
print(f"Dumping conference data to file: {fpath}")
with open(fpath, 'w') as f:
    json.dump(final, f, indent=4)
