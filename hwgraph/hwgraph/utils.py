# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from json import loads

def load_json(fname):
    # I like having comments in JSON.
    with open(fname, 'r') as f:
        lines = [l.strip() for l in f.readlines()]
        lines = [l for l in lines if not l.startswith('//')]
    return loads('\n'.join(lines))
