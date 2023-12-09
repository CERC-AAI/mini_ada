from datetime import datetime

class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def now() -> str:
    """
    Returns a string containing the current date and time
    in the DD.MM.YYYY_HH:MM:SS format
    """

    return datetime.now().strftime("%d.%m.%Y_%H:%M:%S")