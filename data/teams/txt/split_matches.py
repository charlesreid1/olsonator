import os
import json



def dump_matches(matches_file, fwdmap_file, revmap_file):

    with open(matches_file, 'r') as f:
        lines = f.readlines()

    fwd_map = {}
    rev_map = {}
    for line in lines:
        tokens = [j.strip() for j in line.split("|")]
        fwd_map[tokens[0]] = tokens[1]
        rev_map[tokens[1]] = tokens[0]
    
    fpath = os.path.abspath(os.path.join('..', 'json', fwdmap_file))
    print(f"Dumping mapping to file: {fpath}")
    with open(fpath, 'w') as f:
        json.dump(fwd_map, f, indent=4)
    
    fpath = os.path.abspath(os.path.join('..', 'json', revmap_file))
    print(f"Dumping mapping to file: {fpath}")
    with open(fpath, 'w') as f:
        json.dump(rev_map, f, indent=4)

def dump_list(matches_file, fwd_rev, list_file):
    
    with open(matches_file, 'r') as f:
        lines = f.readlines()

    final_list = []
    for line in lines:
        tokens = [j.strip() for j in line.split("|")]
        if fwd_rev=='fwd':
            final_list.append(tokens[0])
        elif fwd_rev=='rev':
            final_list.append(tokens[1])

    fpath = os.path.abspath(os.path.join('..', 'json', list_file))
    print(f"Dumping mapping to file: {fpath}")
    with open(fpath, 'w') as f:
        json.dump(final_list, f, indent=4)


# donchess <--> sagarin
dump_matches('matched_donch_sag.txt', 'donch2sag.json', 'sag2donch.json')

# donchess <--> kenpom
dump_matches('matched_donch_kenpom.txt', 'donch2kenpom.json', 'kenpom2donch.json')

# donchess <--> teamrankings
dump_matches('matched_donch_teamrankings.txt', 'donch2teamrankings.json', 'teamrankings2donch.json')

# non-map lists
dump_list('matched_donch_sag.txt',          'rev', 'sag.json')
dump_list('matched_donch_kenpom.txt',       'rev', 'kenpom.json')
dump_list('matched_donch_teamrankings.txt', 'rev', 'teamrankings.json')
dump_list('matched_donch_kenpom.txt',       'fwd', 'donch.json')

