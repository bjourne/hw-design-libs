# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from collections import defaultdict

class Wire:
    def __init__(self):
        self.arity = None
        self.value = None
        self.destinations = []

    def __repr__(self):
        return 'Wire<%s, %s>' % (self.arity, self.destinations)

class Vertex:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.refer_by_name = False

        self.input = []
        self.output = [Wire() for _ in type.output]

    def __repr__(self):
        return 'Vertex<%s:%s>' % (self.name, self.type)

def connect_vertices(src, pin_idx, dst):
    dst.input.append((src, pin_idx))
    src.output[pin_idx].destinations.append(dst)

# All ops with two inputs.
BINARY_OPS = {
    'and', 'xor', 'or',
    'ge', 'gt',
    'shl',
    'eq', 'sub', 'add'
}
# All ops with one input.
UNARY_OPS = {'not'}

# All ops with two inputs for which the arity of the lhs must match
# the arity of the rhs.
BALANCED_BINARY_OPS = {
    'and', 'xor', 'or',
    # TODO: Fix this (ge vs gt)
    'ge', 'gt',
    'eq', 'sub', 'add'
}

def package_expr(parent, child):
    parent_tp = parent.type.name
    child_tp = child and child.type.name
    if parent_tp in BINARY_OPS:
        if child_tp in BINARY_OPS:
            return '(%s)'
    elif parent_tp == 'cat' and child_tp != 'cat':
        return '{%s}'
    return '%s'
