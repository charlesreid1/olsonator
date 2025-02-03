import math
import json
import os
import pytz
from datetime import datetime


def pythagorean_win_pct(team_points, versus_points, exponent=11.5):
    tp = math.pow(team_points, exponent)
    vp = math.pow(versus_points, exponent)
    wpct = tp/(tp+vp)
    return wpct


def repl(text):
    chars = "'-.& "
    for c in chars:
        text = text.replace(c, "_")
    return text


def load_json(path_to_file, fname):
    """
    Load a list of team names used by a particular site
    """
    fpath = os.path.join(path_to_file, fname)
    with open(fpath, 'r') as f:
        d = json.load(f)
    return d


def assert_required_keys_present(d, keys):
    """
    Check that each key in the list "keys"
    is present in the keys of dictionary d.
    Raise an AssertionError if not.
    """
    for rk in keys:
        if rk not in d.keys():
            raise KeyError(rk)


def get_utc_offset_int(timezone_name):
    """
    Given a datetime timezone name, use pytz to get
    the UTC offset of that timezone in hours.
    Return the integer value.
    """
    try:
        tz = pytz.timezone(timezone_name)
        current_time = datetime.now(tz)
        return int(current_time.strftime('%z'))//100
    except pytz.exceptions.UnknownTimeZoneError:
        raise ValueError(f"Error: pytz could not understand time zone {timezone_name}")


####################################################
# Utility functions related to odds/probability/pct


def american2decimal(s):
    if type(s)==int:
        if s>0:
            s = "+" + str(s)
        else:
            s = str(s)

    sign = s[0]
    mag = float(s[1:])
    p = 0
    if sign=='-':
        p = (mag/(mag+100))
    elif sign=='+':
        p = (100/(mag+100))
    else:
        msg = "Error: american2decimal must receive a string prefixed with + or -"
        raise Exception(msg)
    return p


def decimal2american(d):
    """
    Input: decimal odds (float between 0 and 1).
    Output: american odds (string prefixed with +/-).
    """
    if d > 1.0 or d < 0.0:
        msg = "Error: decimal2american must receive a float between 0 and 1"
        raise Exception(msg)
    if d <= 0.5:
        odds = "+" + str(int(100*(1.0-d)/d))
    elif d > 0.5:
        odds = str(int(100*d/(d-1.0)))
    return odds


def bet_win_american(bet_amt, american_odds):
    """Return the amount a bet would win, given the bet amount and american odds"""
    if type(american_odds)==int:
        if american_odds>0:
            american_odds = "+" + str(american_odds)
        else:
            american_odds = str(american_odds)

    sign = american_odds[0]
    if sign not in ["+", "-"]:
        msg = f"Error: bet_win_american() must take American odds starting with + or -, you provided {american_odds}"
        raise Exception(msg)

    mag = int(american_odds[1:])/100
    if sign=="+":
        return bet_amt*mag
    if sign=="-":
        return bet_amt*(1.0/mag)


def bet_win_decimal(bet_amt, decimal_odds):
    """Return the amount a bet would win, given the bet amount and decimal odds"""
    american_odds = decimal2american(decimal_odds)
    return bet_win_american(bet_amt, american_odds)

def pretty_pct(s):
    return f"{s:0.1f} %"


