import json
import os
from rapidfuzz import fuzz

from .errors import TeamNotFoundException


"""
Utility functions related to team names
"""


PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEAM_DIR = os.path.join(PKG_ROOT, 'data', 'teams', 'json') 


def load_list(fname):
    """
    Load a list of team names used by a particular site
    """
    fpath = os.path.join(TEAM_DIR, fname)
    with open(fpath, 'r') as f:
        names_list = json.load(f)
    return names_list


def get_kenpom_teams():
    return load_list("kenpom.json")


def get_donch_teams():
    return load_list("donch.json")


def get_teamrankings_teams():
    return load_list("teamrankings.json")


def is_kenpom_team(team_name):
    """Is this team name in the Kenpom set of team names?"""
    kenpom_list = get_kenpom_teams()
    return team_name in kenpom_list


def is_donch_team(team_name):
    """Is this team name in the donch set of team names?"""
    donch_list = get_donch_teams()
    return team_name in donch_list


def is_teamrankings_team(team_name):
    """Is this team name in the teamrankings set of team names?"""
    teamrankings_list = get_teamrankings_teams()
    return team_name in teamrankings_list


def lookup(team_name, fname):
    """
    Look up a team name in a given JSON file that maps
    team names from one universe to another, and return
    its corresponding value.

    There are multiple name lookup maps in JSON files,
    so this is a generic function that parameterizes it.
    """
    fpath = os.path.join(TEAM_DIR, fname)
    with open(fpath, 'r') as f:
        names_map = json.load(f)

    # First, check if the name is an exact match
    if team_name in names_map:
        return names_map[team_name]

    # Second, check if case is an issue
    for name in names_map:
        if name.lower()==team_name.lower():
            return names_map[name]

    # Third, see if it is a matter of one or two characters
    for name in names_map:
        if fuzz.partial_ratio(name.lower(), team_name.lower()) > 98:
            return names_map[name]

    # Give up
    raise TeamNotFoundException(f"Could not find Donchess team {team_name}")


def donch2kenpom(name):
    """Convert a donchess school name to a kenpom school name"""
    return lookup(name, fname="donch2kenpom.json")


def kenpom2donch(name):
    """Convert a kenpom school name to a donchess school name"""
    return lookup(name, fname="kenpom2donch.json")


def donch2teamrankings(name):
    """Convert a donchess school name to a teamrankings school name"""
    return lookup(name, fname="donch2teamrankings.json")


def teamrankings2donch(name):
    """Convert a teamrankings school name to a donchess school name"""
    return lookup(name, fname="teamrankings2donch.json")


def normalize_to_teamrankings_names(team_name):
    """
    Whatever name we have, wherever it is from,
    normalize it back to a TeamRankings name
    """
    if is_teamrankings_team(team_name):
        return team_name
    elif is_donch_team(team_name):
        return donch2teamrankings(team_name)
    elif is_kenpom_team(team_name):
        return kenpom2donch(donch2teamrankings(team_name))
    else:
        raise TeamNotFoundException(f"Could not normalize to TeamRankings name: {team_name}")
