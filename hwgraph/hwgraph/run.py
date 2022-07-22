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

def port_get(types, vertices, port):
    if '.' in port:
        name, out = port.split('.')
    else:
        name, out = port, 'o'
    v = vertex_get(vertices, name)
    tp = v.type
    if out not in tp.output:
        raise ValueError(f'No {out} output for {tp.name}')
    return v, out

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
            vertices[n] = Vertex(n, tp)
    for ar, ns in circuit['arities'].items():
        ar = int(ar)
        for n in ns:
            vertex_get(vertices, n).arity = ar

    for v_to, ports in circuit['inputs'].items():
        v_to = vertex_get(vertices, v_to)
        for port in ports:
            v_from, out = port_get(types, vertices, port)
            connect_vertices(v_from, out, v_to)
            # v_to.input.append((v_from, out))
            # v_from.output[out].wires.append(v_to)

    for n, v in circuit.get('values', {}).items():
        vertices[n].value = v

    for n in circuit['refer_by_name']:
        vertices[n].refer_by_name = True
    return vertices.values()
    # return sorted(vertices.values(),
    #               key = lambda v: (v.type.name, v.arity or 0, v.name))

def check_vertex(v):
    tp, n = v.type, v.name
    inputs = [i.name for i in v.inputs]
    disc = tp.input[len(inputs):]
    fmt = 'Vertex %s has disconnected inputs: %s'
    if disc:
        raise ValueError(fmt % (n, ', '.join(disc)))

    fmt = 'Constant %s has no value'
    if tp.name == 'const' and v.value is None:
        raise ValueError(fmt % n)

    fmt = 'Vertex %s has disconnected outputs: %s'
    outs = [n for (n, out) in v.outputs.items() if not out.wires]
    if outs:
        raise ValueError(fmt % (n, ', '.join(outs)))

    fmt = 'Vertex %s has superfluous inputs: %s'
    extra = inputs[len(tp.input):]
    if extra:
        raise ValueError(fmt % (n, ', '.join(extra)))

def main():
    types_path, circuit_path, test_path = [Path(p) for p in argv[1:]]
    circuit_name = circuit_path.stem

    types = load_types(types_path)

    vertices = load_circuit(circuit_path, types)

    for v in vertices:
        check_vertex(v)

    infer_arities(vertices)

    return

    OUTPUT.mkdir(exist_ok = True)
    render_module(vertices, circuit_name, OUTPUT)

    tests = load_json(test_path)
    shuffle(tests)

    render_tb(vertices, tests, circuit_name, OUTPUT)

    path = OUTPUT / f'{circuit_name}.png'
    plot_vertices(vertices, path, False, True, True)

    path = OUTPUT / f'{circuit_name}_statements.png'
    plot_expressions(vertices, path, True)

main()
