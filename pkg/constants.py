import os
from .utils import load_json


PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEAM_DIR = os.path.join(PKG_ROOT, 'data', 'teams', 'json')


##########################
# Name-related constants

DONCH_TEAMS  = load_json(TEAM_DIR, 'donch.json')
KENPOM_TEAMS = load_json(TEAM_DIR, 'kenpom.json')
TR_TEAMS     = load_json(TEAM_DIR, 'teamrankings.json')

# Mappings from one to the other
DONCH2KENPOM_MAP = load_json(TEAM_DIR, 'donch2kenpom.json')
KENPOM2DONCH_MAP = load_json(TEAM_DIR, 'kenpom2donch.json')

DONCH2TR_MAP = load_json(TEAM_DIR, 'donch2teamrankings.json')
TR2DONCH_MAP = load_json(TEAM_DIR, 'teamrankings2donch.json')


##########################
# Geographic data

GEO_CITIES  = load_json(TEAM_DIR, 'geo_cities.json')
GEO_LATLONG = load_json(TEAM_DIR, 'geo_latlong.json')


##########################
# Sport-related constants

# How many points does home court advantage afford
HOME_ADVANTAGE = 3.09

