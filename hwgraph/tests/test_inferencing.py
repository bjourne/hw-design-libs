# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from hwgraph import Type, Vertex, connect_vertices
from hwgraph.inferencing import forward, input_arities

def test_input_arities():
    c1 = Vertex('c1', Type('const', [], ['o']))
    c1.output['o'].arity = 5
    add = Vertex('sum', Type('add', ['i1', 'i2'], ['o']))

    connect_vertices(c1, 'o', add)
    connect_vertices(c1, 'o', add)
    assert input_arities(add) == [5, 5]

def test_forward_add():
    c1 = Vertex('c1', Type('const', [], ['o']))
    c1.output['o'].arity = 5
    add = Vertex('v', Type('add', ['i1', 'i2'], ['o']))

    connect_vertices(c1, 'o', add)
    connect_vertices(c1, 'o', add)
    assert forward(add)

    assert add.output['o'].arity == 5

def test_forward_cat():
    c1 = Vertex('c1', Type('const', [], ['o']))
    c1.output['o'].arity = 5
    cat = Vertex('v', Type('cat', ['i1', 'i2'], ['o']))

    connect_vertices(c1, 'o', cat)
    connect_vertices(c1, 'o', cat)
    assert forward(cat)

    assert cat.output['o'].arity == 10
