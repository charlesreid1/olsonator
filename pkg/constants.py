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
    A10  = 24.9,
    ACC  = 15.6,
    AE   = 29.3,
    ASun = 14.8,
    Amer = 28.3,
    B10  = 26.5,
    B12  = 23.8,
    BE   = 17.3,
    BSky = 16.7,
    BSth = 18.2,
    BW   = 22.2,
    CAA  = 28.7,
    CUSA = 13.9,
    Horz = 28.2,
    Ivy  = 27.3,
    MAAC = 12.6,
    MAC  = 18.4,
    MEAC = 4.5,
    MVC  = 20.8,
    MWC  = 20.6,
    NEC  = 23.9,
    OVC  = 20.2,
    PL   = 9.3,
    SB   = 21.3,
    SC   = 31.2,
    SEC  = 11.8,
    SWAC = 18.6,
    Slnd = 23.4,
    Sum  = 21.5,
    WAC  = 18.3,
    WCC  = 17.3,
)

