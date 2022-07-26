# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from hwgraph import Type, Vertex, connect_vertices
from hwgraph.inferencing2 import constrain

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




# def test_input_arities():
#     c1 = Vertex('c1', Type('const', [], ['o']))
#     c1.output['o'].arity = 5
#     add = Vertex('sum', Type('add', ['i1', 'i2'], ['o']))

#     connect_vertices(c1, 'o', add)
#     connect_vertices(c1, 'o', add)
#     assert input_arities(add) == [5, 5]

# def test_forward_add():
#     c1 = Vertex('c1', Type('const', [], ['o']))
#     c1.output['o'].arity = 5
#     add = Vertex('v', Type('add', ['i1', 'i2'], ['o']))

#     connect_vertices(c1, 'o', add)
#     connect_vertices(c1, 'o', add)
#     assert forward(add)

#     assert add.output['o'].arity == 5

# def test_forward_cat():
#     c1 = Vertex('c1', Type('const', [], ['o']))
#     c1.output['o'].arity = 5
#     cat = Vertex('v', Type('cat', ['i1', 'i2'], ['o']))

#     connect_vertices(c1, 'o', cat)
#     connect_vertices(c1, 'o', cat)
#     assert forward(cat)

#     assert cat.output['o'].arity == 10
