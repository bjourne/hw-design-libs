# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from hwgraph import Type, Vertex, connect_vertices
from hwgraph.algebra import constrain
from hwgraph.inferencing import infer

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

def test_div():
    vars = {'lo' : 5}
    assert constrain(vars, 'lo/5 == o') == ('o', '==', 1)

TYPE_CAT = Type('cat', ['i1', 'i2'], ['o'], ['i1 + i2 == o'])
TYPE_ADD = Type('add', ['i1', 'i2'], ['o'], ['i1 == i2', 'i2 == o'])
TYPE_CONST = Type('const', [], ['o'], [])
TYPE_FULL_ADDER = Type('fa',
                       ['a', 'b', 'ci'],
                       ['s', 'co'],
                       ['a == b'])


def test_forward_cat():
    c1 = Vertex('c1', TYPE_CONST)
    c1.output['o'].arity = 5
    v = Vertex('v', TYPE_CAT)

    connect_vertices(c1, 'o', v)
    connect_vertices(c1, 'o', v)
    assert infer(v)
    assert v.output['o'].arity == 10

def test_backward_cat():
    c1 = Vertex('c1', TYPE_CONST)
    c2 = Vertex('c2', TYPE_CONST)
    c1.output['o'].arity = 5
    v = Vertex('v', TYPE_CAT)
    v.output['o'].arity = 20

    connect_vertices(c1, 'o', v)
    connect_vertices(c2, 'o', v)
    assert infer(v)
    assert c2.output['o'].arity == 15

def test_forward_add():
    c1 = Vertex('c1', TYPE_CONST)
    c1.output['o'].arity = 5
    v = Vertex('v', TYPE_ADD)
    connect_vertices(c1, 'o', v)
    connect_vertices(c1, 'o', v)
    assert infer(v)
    assert v.output['o'].arity == 5

def test_backward_add():
    c1 = Vertex('c1', TYPE_CONST)
    c2 = Vertex('c2', TYPE_CONST)
    c1.output['o'].arity = 5
    v = Vertex('v', TYPE_ADD)
    connect_vertices(c1, 'o', v)
    connect_vertices(c2, 'o', v)
    v.output['o'].arity = 10
    try:
        assert infer(v)
        assert False
    except ValueError:
        pass

def test_full_adder():
    fa = Vertex('fa', TYPE_FULL_ADDER)
    assert not infer(fa)
