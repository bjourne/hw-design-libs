# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
class Vertex:
    def __init__(self, name, type, arity, value):
        self.name = name
        self.type = type
        self.arity = arity
        self.predecessors = []
        self.value = value
        self.refer_by_name = False

        # We don't yet support vertices with multiple outputs.
        self.successors = []

    def __repr__(self):
        return 'Vertex<%s:%s:%s>' % (self.name, self.type, self.arity or '?')

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
        elif child_tp == 'cat':
            return "%d'(%%s)" % parent.arity
    elif parent_tp == 'cat' and child_tp != 'cat':
        return '{%s}'
    return '%s'
