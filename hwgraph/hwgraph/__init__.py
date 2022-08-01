# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
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
