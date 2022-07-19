"""Utility to call functions with csv."""


import csv

import argparse
from pathlib import Path
import os


_TRUE_FLAG="TRUE"


def read_csv(file, newline=''):
    with open(file, newline=newline) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        # Creates a list of lines in csv file.
        parameters = [*reader]
    return parameters 


def _maybe_none(line):
    """Parses `none` values in CSV."""
    return [None if item=='' else item for item in line]


# TODO: Handle blank entries.
def parse_csv(file, headerline=0, skiplines=None, readcolumns=None, **kwargs):
    """Parses csv and returns a list of `dict` for each line.

    The keys of the dict are given by the entries in columns of `headerline`.

    args:
        file: Path to csv file.
        headerline: int, specifies line that contains dictionary keys.
        skiplines: Optionally, specifies rows of csv to skip.
        columns: Optionally, specify columns to read. Should be a valid list Selection.

    returns:
        csv_args: `List` of `dict` containing parsed csv entries.
    """
    if skiplines is None:
        skiplines = []

    csv_lines = read_csv(file)

    # Select columns.
    if readcolumns is not None:
        csv_lines = [c[readcolumns] for c in csv_lines]

    # Get keys.
    keys = csv_lines[headerline]

    skiplines.append(headerline)
    if check_duplicate(skiplines):
        raise ValueError("`skiplines` contains duplicates.")

    # Remove ignore lines.
    [csv_lines.pop(i) for i in sorted(skiplines, reverse=True)]

    # Parse `None`
    csv_lines = [_maybe_none(line) for line in csv_lines]

    csv_args = []
    for line in csv_lines:
        csv_args.append(dict(zip(keys, line)))
    return csv_args


def check_duplicate(a):
    """Returns `True` if `a` contains duplicate items."""
    d = set([x for x in a if a.count(x) > 1])
    return len(d) > 0


def dict_to_CLI_args(
    d: dict,
):
    argstring = []
    for k, v in d.items():
        _check_CLI_key(k)
        if isinstance(v, str):
            # If the string is `$TRUE_FLAG` then use as a boolean argument.
            if v==_TRUE_FLAG:
                argstring.append(f"--{k}")
            else:
                argstring.append(f"--{k} {v}")
        elif v is None:
            # If a blank value, then don't add anything to CLI args.
            pass
        else:
            # Format as float.
            argstring.append(f"--{k} {v:.1E}")

    return " ".join(argstring)

def _check_CLI_key(k):
    """Confirms key is a `str`."""
    if not isinstance(k, str):
        raise ValueError("All argument keys must be `str`.")
