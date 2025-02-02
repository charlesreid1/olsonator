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

# Conferences
CONFERENCES  = load_json(TEAM_DIR, 'team_conferences.json')



##########################
# Geographic data

GEO_CITIES  = load_json(TEAM_DIR, 'geo_cities.json')
GEO_LATLONG = load_json(TEAM_DIR, 'geo_latlong.json')


########################################
# Constants related to factors/modifiers

# How many points does home court advantage afford
HOME_ADVANTAGE = 3.09


#######################################
# Relative confidence levels 
# for predictions of this conference

CONFIDENCES = dict(
    A10=0,
    ACC=-10,
    AE=-4,
    ASun=-13,
    Amer=7,
    B10=-9,
    B12=-7,
    BE=0,
    BSky=7,
    BSth=-6,
    BW=-14,
    CAA=-7,
    CUSA=15,
    Horz=-3,
    Ivy=4,
    MAAC=-1,
    MAC=-12,
    MEAC=-1,
    MVC=-2,
    MWC=-3,
    NEC=-10,
    OVC=-7,
    PL=2,
    SB=0,
    SC=-17,
    SEC=6,
    SWAC=-9,
    Slnd=11,
    Sum=-14,
    WAC=2,
    WCC=3,
)

