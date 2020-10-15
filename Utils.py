from datetime import datetime

import pytz


def escape(input_string):
    return input_string.translate(input_string.maketrans({"(": r"\(",
                                                          ")": r"\)",
                                                          "-": r"\-",
                                                          "]": r"\]",
                                                          "\\": r"\\",
                                                          "^": r"\^",
                                                          "$": r"\$",
                                                          "*": r"\*",
                                                          ".": r"\."}))


def string2datetime(input):
    if isinstance(input, str):
        return pytz.timezone("Europe/Rome").localize(datetime.strptime(input, "%Y-%m-%dT%H:%M:%S"))
    else:
        return pytz.timezone("Europe/Rome").localize(input)