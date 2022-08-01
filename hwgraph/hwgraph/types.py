# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from hwgraph.utils import load_json
from pathlib import Path

class Type:
    def __init__(self, name, input, output, constraints,
                 is_module, optional_outputs):
        self.name = name
        self.input = input
        self.output = output
        self.constraints = constraints
        self.is_module = is_module
        self.optional_outputs = optional_outputs

    def __repr__(self):
        fmt = '%s[(%s) -> (%s)]'
        args = self.name, ', '.join(self.input), ', '.join(self.output)
        return fmt % args

TYPES_LOADED = False
TYPES_PATH = Path('examples/types.json')
TYPES = None

def type_get(name):
    tp = TYPES.get(name)
    if not tp:
        raise ValueError(f'Missing type: {name}')
    return tp

def load_types(path):
    print(f'Loading types from {path}.')
    d1 = load_json(path)
    types = {}
    for n, d2 in d1.items():
        types[n] = Type(
            n,
            d2['input'],
            d2['output'],
            d2['constraints'],
            d2.get('is_module') or False,
            d2.get('optional_outputs') or False
        )
    return types

if not TYPES_LOADED:
    TYPES = load_types(TYPES_PATH)
    TYPES_LOADED = True
