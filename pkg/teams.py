import json
import os
from rapidfuzz import fuzz

from .constants import (
    DONCH_TEAMS,
    KENPOM_TEAMS,
    TR_TEAMS,
    DONCH2KENPOM_MAP,
    KENPOM2DONCH_MAP,
    DONCH2TR_MAP,
    TR2DONCH_MAP,
)
from .errors import TeamNotFoundException


"""
Utility functions related to team names and geography
"""


def get_kenpom_teams():
    return KENPOM_TEAMS


def get_donch_teams():
    return DONCH_TEAMS


def get_teamrankings_teams():
    return TR_TEAMS


def is_kenpom_team(team_name):
    """Is this team name in the Kenpom set of team names?"""
    kenpom_list = get_kenpom_teams()
    return team_name in kenpom_list


def is_donch_team(team_name):
    """Is this team name in the donch set of team names?"""
    return team_name in DONCH_TEAMS


def is_teamrankings_team(team_name):
    """Is this team name in the teamrankings set of team names?"""
    return team_name in TR_TEAMS


def lookup(team_name, names_map):
    """
    Look up a team name in a given JSON file that maps
    team names from one universe to another, and return
    its corresponding value.

    There are multiple name lookup maps in JSON files,
    so this is a generic function that parameterizes it.
    """
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
    return DONCH2KENPOM_MAP[name]


def kenpom2donch(name):
    """Convert a kenpom school name to a donchess school name"""
    return KENPOM2DONCH_MAP[name]


def donch2teamrankings(name):
    """Convert a donchess school name to a teamrankings school name"""
    return DONCH2TR_MAP[name]


def teamrankings2donch(name):
    """Convert a teamrankings school name to a donchess school name"""
    return TR2DONCH_MAP[name]


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
        return donch2teamrankings(kenpom2donch(team_name))
    else:
        raise TeamNotFoundException(f"Could not normalize to TeamRankings name: {team_name}")


def normalize_to_donchess_names(team_name):
    """
    Whatever name we have, wherever it is from,
    normalize it back to a TeamRankings name
    """
    if is_donch_team(team_name):
        return team_name
    elif is_teamrankings_team(team_name):
        return teamrankings2donch(team_name)
    elif is_kenpom_team(team_name):
        return kenpom2donch(team_name)
    else:
        raise TeamNotFoundException(f"Could not normalize to Donchess name: {team_name}")


def get_school_latlong(team_name):
    team_name = teamrankings2donch(normalize_to_teamrankings_names(team_name))
    return GEO_LATLONG[team_name]


def get_school_city(team_name):
    team_name = teamrankings2donch(normalize_to_teamrankings_names(team_name))
    return GEO_CITIES[team_name]

