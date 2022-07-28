# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from hwgraph import Vertex, connect_vertices
from hwgraph.algebra import constrain
from hwgraph.inferencing import infer_vertex
from hwgraph.types import TYPES

def test_no_solutions():
    assert constrain({}, '10 < 0') == 'nosol'
    assert constrain({}, '0 < 0') == 'nosol'
    assert constrain({}, '3 < 3') == 'nosol'
    assert constrain({}, '3 > 3') == 'nosol'
    assert constrain({}, '-10 > 0') == 'nosol'
    assert constrain({}, '-10 > -5') == 'nosol'
    assert constrain({}, '10 == 5') == 'nosol'

    assert constrain({'x' : 3}, 'x == 5') == 'nosol'
    assert constrain({'x' : 3}, 'x > 5') == 'nosol'

def test_many_solutions():
    assert constrain({}, 'x > y') == 'many'

def test_satisfies():
    assert constrain({}, '10 > 0') == 'satisfies'
    assert constrain({}, '-10 > -11') == 'satisfies'
    vars = {'hi' : 3, 'lo' : 0}
    assert constrain(vars, 'hi > lo') == 'satisfies'

    vars = {'i' : 9, 'n.value' : 8}
    assert constrain(vars, 'i >= n.value') == 'satisfies'
    assert constrain(vars, 'n.value <= i') == 'satisfies'

def test_basic():
    vars = {'hi' : 20, 'lo' : 9}
    res = constrain(vars, 'hi - lo == o')
    assert res == ('o', '==', 11)

    vars = {'hi' : 20, 'lo' : 9, 'o' : 50}
    res = constrain(vars, 'hi - lo == o')
    assert res == 'nosol'

    res = constrain({}, 'hi - lo == o')
    assert res == 'many'

    vars = {'n' : 3}
    assert constrain(vars, 'n == i') == ('i', '==', 3)

def test_ineqs():
    vars = {'lo' : 5}
    assert constrain(vars, 'hi > lo') == ('hi', '>', 5)
    assert constrain({}, '8 > o') == ('o', '<', 8)
    assert constrain({}, '8 > -o') == ('o', '>', -8)
    assert constrain({}, '-8 > o') == ('o', '<', -8)
    assert constrain({}, '-8 > -o') == ('o', '>', 8)

    assert constrain({}, '8 < o') == ('o', '>', 8)
    assert constrain({}, '8 < -o') == ('o', '<', -8)
    assert constrain({}, '-8 < o') == ('o', '>', -8)
    assert constrain({}, '-8 < -o') == ('o', '<', 8)

def test_gte_or_lte():
    vars = {'lo' : None}
    assert constrain(vars, 'lo >= 3') == ('lo', '>=', 3)
    assert constrain(vars, '-lo >= 3') == ('lo', '<=', -3)
    assert constrain(vars, 'lo >= -3') == ('lo', '>=', -3)
    assert constrain(vars, '-lo >= -3') == ('lo', '<=', 3)

    assert constrain(vars, 'lo <= 3') == ('lo', '<=', 3)
    assert constrain(vars, 'lo <= -3') == ('lo', '<=', -3)
    assert constrain(vars, '-lo <= 3') == ('lo', '>=', -3)
    assert constrain(vars, '-lo <= -3') == ('lo', '>=', 3)

def test_div():
    vars = {'lo' : 5}
    assert constrain(vars, 'lo/5 == o') == ('o', '==', 1)

def test_infer_attributes():
    vars = {'lo.value' : 3, 'hi.value' : 8,
            'o' : None}
    expr = 'hi.value - lo.value + 1 == o'
    assert constrain(vars, expr) == ('o', '==', 6)

def test_forward_cat():
    c1 = Vertex('c1', TYPES['const'])
    c1.output[0].arity = 5
    v = Vertex('v', TYPES['cat'])

    connect_vertices(c1, 0, v)
    connect_vertices(c1, 0, v)
    assert infer_vertex(v)
    assert v.output[0].arity == 10

def test_backward_cat():
    c1 = Vertex('c1', TYPES['const'])
    c2 = Vertex('c2', TYPES['const'])
    c1.output[0].arity = 5
    v = Vertex('v', TYPES['cat'])
    v.output[0].arity = 20

    connect_vertices(c1, 0, v)
    connect_vertices(c2, 0, v)
    assert infer_vertex(v)
    assert c2.output[0].arity == 15

def test_forward_add():
    c1 = Vertex('c1', TYPES['const'])
    c1.output[0].arity = 5
    v = Vertex('v', TYPES['add'])
    connect_vertices(c1, 0, v)
    connect_vertices(c1, 0, v)
    assert infer_vertex(v)
    assert v.output[0].arity == 5

def test_backward_add():
    c1 = Vertex('c1', TYPES['const'])
    c2 = Vertex('c2', TYPES['const'])
    c1.output[0].arity = 5
    v = Vertex('v', TYPES['add'])
    connect_vertices(c1, 0, v)
    connect_vertices(c2, 0, v)
    v.output[0].arity = 10
    try:
        assert infer_vertex(v)
        assert False
    except ValueError:
        pass

def test_full_adder():
    fa = Vertex('fa', TYPES['full_adder'])
    assert infer_vertex(fa)

def test_value_inferencing():
    sl = Vertex('sl', TYPES['slice'])
    assert not infer_vertex(sl)

    c0 = Vertex('c0', TYPES['const'])
    c1 = Vertex('c1', TYPES['const'])
    c2 = Vertex('c2', TYPES['const'])
    connect_vertices(c0, 0, sl)
    connect_vertices(c1, 0, sl)
    connect_vertices(c2, 0, sl)

    c1.output[0].value = 10
    c2.output[0].value = 5

    assert infer_vertex(sl)
    assert sl.output[0].arity == 6

def test_infer_cast():
    n = Vertex('c0', TYPES['const'])
    i = Vertex('c1', TYPES['const'])
    cast = Vertex('v', TYPES['cast'])

    connect_vertices(n, 0, cast)
    connect_vertices(i, 0, cast)

    n.output[0].value = 8
    cast.output[0].arity = 8

    # Not enough to infer arity of i.
    assert not infer_vertex(cast)
