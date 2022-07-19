# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from collections import defaultdict
from hwgraph import (
    BINARY_OPS, BALANCED_BINARY_OPS,
    DEFAULT_INT_ARITY,
    UNARY_OPS,
    Type, Vertex)
from hwgraph.plotting import plot_vertices, plot_expressions
from hwgraph.verilog import render_module, render_tb
from json import loads
from pathlib import Path
from random import shuffle
from sys import argv

COMPARE_OPS = {'ge', 'gt', 'eq'}
ARITH_OPS = {'and', 'xor', 'or', 'sub', 'add'}
OUTPUT = Path('output')

def load_json(fname):
    # I like having comments in JSON.
    with open(fname, 'r') as f:
        lines = [l.strip() for l in f.readlines()]
        lines = [l for l in lines if not l.startswith('//')]
    return loads('\n'.join(lines))

def assert_arity(v, arity):
    if v.arity == arity:
        return False
    elif v.arity is None:
        v.arity = arity
        return True
    print(v, arity)
    print("%s incompatible with arity %d." % (v, arity))
    print('Preds/succs: %s' % (v.predecessors, v.successors))
    assert False

def infer_arity_fwd(v):
    tp = v.type.name
    ps = [p for p in v.predecessors]
    arities = [p.arity for p in ps]
    if tp in {'if', 'reg'}:
        arities = arities[1:]
        ps = ps[1:]
    if tp == 'cat':
        if all(arities):
            return assert_arity(v, sum(arities))
    elif tp == 'cast':
        return assert_arity(v, ps[0].value)
    elif tp == 'slice':
        hi = int(ps[1].value)
        lo = int(ps[2].value)
        return assert_arity(v, hi - lo + 1)
    elif tp in {'if', 'reg'} | ARITH_OPS | UNARY_OPS:
        if len(set(arities)) == 1 and arities[0]:
            return assert_arity(v, arities[0])
    elif tp in COMPARE_OPS:
        return assert_arity(v, 1)
    return False

def infer_arity_bwd(v):
    data_ps = v.predecessors
    tp = v.type.name
    arity = v.arity
    if tp in {'if', 'reg', 'slice'}:
        data_ps = data_ps[1:]

    if tp in {'output'} | UNARY_OPS:
        return assert_arity(data_ps[0], arity)
    if tp in BALANCED_BINARY_OPS | {'if', 'slice'}:
        v1, v2 = data_ps
        ar1, ar2 = v1.arity, v2.arity
        changed = False
        if ar1:
            changed = assert_arity(v2, ar1)
        if ar2:
            changed = changed or assert_arity(v1, ar2)
        if tp == 'slice':
            for p in data_ps:
                if len(set(p.successors)) == 1 and not p.arity:
                    p.arity = DEFAULT_INT_ARITY
                    changed = True
        return changed
    elif tp == 'cat':
        ps_arities = [p.arity for p in data_ps]
        if arity and ps_arities.count(None) == 1:
            inferred_arity = arity - sum(p for p in ps_arities if p)
            v = data_ps[ps_arities.index(None)]
            return assert_arity(v, inferred_arity)
        return False

def infer_arities(vertices):
    changed = True
    while changed:
        changed = False
        for v in vertices:
            changed = changed or infer_arity_fwd(v)
        for v in vertices:
            changed = changed or infer_arity_bwd(v)

    missing = [v for v in vertices if not v.arity]
    fmt = 'Cannot infer arities for %s. Explicit declaration necessary.'
    if missing:
        raise ValueError(fmt % ', '.join(v.name for v in missing))

def vertex_get(vertices, name):
    v = vertices.get(name)
    if not v:
        raise ValueError(f'Missing vertex: {name}')
    return v

def type_get(types, name):
    tp = types.get(name)
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
            d2['input'], d2['output']
        )
    return types

def load_circuit(path, types):
    print(f'Loading circuit from {path}.')
    circuit = load_json(path)
    vertices = {}
    for tp_name, ns in circuit['types'].items():
        tp = type_get(types, tp_name)
        for n in ns:
            vertices[n] = Vertex(n, tp, None, None)
    for ar, ns in circuit['arities'].items():
        ar = int(ar)
        for n in ns:
            vertex_get(vertices, n).arity = ar
    for n, ps in circuit['predecessors'].items():
        ps = [vertex_get(vertices, p) for p in ps]
        v = vertex_get(vertices, n)
        v.predecessors = ps
        for p in ps:
            p.successors.append(v)
    for n, v in circuit.get('values', {}).items():
        vertices[n].value = v

    for n in circuit['refer_by_name']:
        vertices[n].refer_by_name = True
    return sorted(vertices.values(),
                  key = lambda v: (v.type.name, v.arity or 0, v.name))

def check_vertex(v):
    tp, n = v.type, v.name
    preds = [p.name for p in v.predecessors]
    disc = tp.input[len(preds):]
    fmt = 'Vertex %s has disconnected inputs: %s'
    if disc:
        raise ValueError(fmt % (n, ', '.join(disc)))

    fmt = 'Constant %s has no value'
    if tp.name == 'const' and v.value is None:
        raise ValueError(fmt % n)

    fmt = 'Vertex %s has disconnected outputs: %s'
    if tp.output and not v.successors:
        raise ValueError(fmt % (n, ', '.join(tp.output)))

    fmt = 'Vertex %s has superfluous inputs: %s'
    extra = preds[len(tp.input):]
    if extra:
        raise ValueError(fmt % (n, ', '.join(extra)))

def check_vertices(vertices):
    for v in vertices:
        check_vertex(v)

def main():
    types_path, circuit_path, test_path = [Path(p) for p in argv[1:]]
    circuit_name = circuit_path.stem

    types = load_types(types_path)

    vertices = load_circuit(circuit_path, types)
    check_vertices(vertices)

    infer_arities(vertices)

    OUTPUT.mkdir(exist_ok = True)
    render_module(vertices, circuit_name, OUTPUT)

    tests = load_json(test_path)
    shuffle(tests)

    render_tb(vertices, tests, circuit_name, OUTPUT)

    path = OUTPUT / f'{circuit_name}.png'
    plot_vertices(vertices, path, False, False, True)

    path = OUTPUT / f'{circuit_name}_statements.png'
    plot_expressions(vertices, path)

main()
