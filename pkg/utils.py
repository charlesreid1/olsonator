import json
import os
import pytz
from datetime import datetime


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

