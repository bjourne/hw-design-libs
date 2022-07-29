# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from itertools import groupby
from json import loads

# How much to indent stuff
BASE_INDENT = 4

def load_json(fname):
    # I like having comments in JSON.
    with open(fname, 'r') as f:
        lines = [l.strip() for l in f.readlines()]
        lines = [l for l in lines if not l.startswith('//')]
    return loads('\n'.join(lines))

def groupby_sort(seq, keyfun):
    seq = sorted(seq, key = keyfun)
    grps = groupby(seq, keyfun)
    grps = [(k, list(v)) for k, v in grps]
    return sorted(grps)

def long_value_error(header, lines):
    lines = [header] + [' ' * BASE_INDENT + l for l in lines]
    raise ValueError('\n'.join(lines))

def flatten(seq):
    return [y for x in seq for y in x]
