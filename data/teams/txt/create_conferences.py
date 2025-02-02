import os
import json


def reverse_lookup(v, d):
    result = []
    for k, v2 in d.items():
        if v2==v:
            result.append(k)
    return result


with open('matched_donch_kenpom.txt', 'r') as f:
    lines = f.readlines()

donch2kp = {}
for line in lines:
    tokens = [j.strip() for j in line.split("|")]
    donch2kp[tokens[0]] = tokens[1]

with open('team_conferences.txt', 'r') as f:
    lines = f.readlines()

final = {}
for line in lines:
    tokens = [j.strip() for j in line.split("\t")]
    if tokens[0] in donch2kp.values():
        lea = tokens[1]
        donchs = reverse_lookup(tokens[0], donch2kp)
        for donch in donchs:
            final[donch] = lea

fpath = os.path.abspath(os.path.join('..', 'json', 'team_conferences.json'))
print(f"Dumping conference data to file: {fpath}")
with open(fpath, 'w') as f:
    json.dump(final, f, indent=4)
