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

SPREAD_CONFIDENCES = dict(
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

OU_CONFIDENCES = dict(
    A10  = 10.2,
    ACC  = 21.3,
    AE   = 15.1,
    ASun = 18.5,
    Amer = 21.3,
    B10  = 26.8,
    B12  = 25.6,
    BE   = 22.7,
    BSky = 11.7,
    BSth = 26.8,
    BW   = 19.8,
    CAA  = 15.4,
    CUSA = 18.0,
    Horz = 8.3,
    Ivy  = 25.4,
    MAAC = 26.2,
    MAC  = 25.7,
    MEAC = 35.1,
    MVC  = 22.0,
    MWC  = 15.7,
    NEC  = 28.2,
    OVC  = 26.5,
    PL   = 14.0,
    SB   = 22.2,
    SC   = 12.9,
    SEC  = 22.0,
    SWAC = 26.8,
    Slnd = 11.4,
    Sum  = 35.6,
    WAC  = 6.5,
    WCC  = 18.9,
)

ML_CONFIDENCES = dict(
    A10  = 17.3,
    ACC  = 12.4,
    AE   = 17.1,
    ASun = 18.6,
    Amer = 25.8,
    B10  = 10.9,
    B12  = 22.9,
    BE   = 17.8,
    BSky = 7.8,
    BSth = 17.0,
    BW   = 23.3,
    CAA  = 21.7,
    CUSA = 20.7,
    Horz = 22.0,
    Ivy  = 17.6,
    MAAC = 9.5,
    MAC  = 10.4,
    MEAC = 3.0,
    MVC  = 23.3,
    MWC  = 27.8,
    NEC  = 34.4,
    OVC  = 7.7,
    PL   = 10.9,
    SB   = 18.6,
    SC   = 21.0,
    SEC  = 3.9,
    SWAC = 2.5,
    Slnd = 16.6,
    Sum  = 28.9,
    WAC  = 14.8,
    WCC  = 24.5,
)

