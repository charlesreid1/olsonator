def repl(text):
    chars = "'-.& "
    for c in chars:
        text = text.replace(c, "_")
    return text

def assert_required_keys_present(d, keys):
    """
    Check that each key in the list "keys"
    is present in the keys of dictionary d.
    Raise an AssertionError if not.
    """
    for rk in keys:
        if rk not in d.keys():
            raise KeyError(rk)
