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
        self.internalized = {}

    def __repr__(self):
        return 'Vertex<%s:%s:%s>' % (self.name, self.type, self.arity or '?')

# By nr of arguments
BINARY_OPS = {'and', 'xor', 'or', 'ge', 'eq', 'sub', 'add'}
UNARY_OPS = {'not'}

TYPE_TO_SYMBOL = {
    'and' : '&',
    'xor' : '^',
    'or' : '|',
    'ge' : '>',
    'eq' : '==',
    'sub' : '-',
    'add' : '+',
    'not' : '!'
}
