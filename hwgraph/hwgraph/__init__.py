# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from collections import defaultdict
class Type:
    def __init__(self, name, input, output, constraints):
        self.name = name
        self.input = input
        self.output = output
        self.constraints = constraints

    def __repr__(self):
        fmt = '%s[(%s) -> (%s)]'
        args = self.name, ', '.join(self.input), ', '.join(self.output)
        return fmt % args

class Wire:
    def __init__(self):
        self.arity = None
        self.value = None
        self.destinations = []

class Vertex:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.refer_by_name = False

        self.input = []
        self.output = {n : Wire() for n in type.output}

    def __repr__(self):
        return 'Vertex<%s:%s>' % (self.name, self.type)

def connect_vertices(v_from, out, v_to):
    v_to.input.append((v_from, out))
    v_from.output[out].destinations.append(v_to)

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

DEFAULT_INT_ARITY = 20

TYPE_TO_SYMBOL = {
    'and' : '&',
    'xor' : '^',
    'or' : '|',
    'ge' : '>=',
    'gt' : '>',
    'eq' : '==',
    'shl' : '<<',
    'sub' : '-',
    'add' : '+',
    'not' : '!'
}

def package_vertex(parent, child):
    parent_tp = parent.type.name
    child_tp = child and child.type.name
    if parent_tp in BINARY_OPS:
        if child_tp in BINARY_OPS:
            return '(%s)'
    elif parent_tp == 'cat' and child_tp != 'cat':
        return '{%s}'
    return '%s'
