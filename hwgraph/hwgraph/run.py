# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from collections import defaultdict
from hwgraph import (
    BINARY_OPS, BALANCED_BINARY_OPS,
    UNARY_OPS,
    Vertex,
    connect_vertices)

from hwgraph.inferencing import infer_vertices
from hwgraph.plotting import plot_vertices, plot_expressions
from hwgraph.types import type_get
from hwgraph.utils import load_json
from hwgraph.verilog import render_module, render_tb
from pathlib import Path
from random import shuffle
from sys import argv

OUTPUT = Path('output')

def vertex_get(vertices, name):
    v = vertices.get(name)
    if not v:
        raise ValueError(f'Missing vertex: {name}')
    return v

def port_get(vertices, port):
    if '.' in port:
        name, out = port.split('.')
    else:
        name, out = port, 'o'
    v = vertex_get(vertices, name)
    tp = v.type

    if out not in tp.output:
        err = 'Vertex %s:%s has no %s output'
        raise ValueError(err % (v.name, tp.name, out))
    return v, tp.output.index(out)

def load_circuit(path):
    print(f'Loading circuit from {path}.')
    circuit = load_json(path)
    vertices = {}
    for tp_name, ns in circuit['types'].items():
        tp = type_get(tp_name)
        for n in ns:
            vertices[n] = Vertex(n, tp)
    for ar, ns in circuit['arities'].items():
        ar = int(ar)
        for n in ns:
            v, pin = port_get(vertices, n)
            v.output[pin].arity = ar

    for v_to, ports in circuit['inputs'].items():
        v_to = vertex_get(vertices, v_to)
        for port in ports:
            v_from, out = port_get(vertices, port)
            connect_vertices(v_from, out, v_to)

    for n, v in circuit.get('values', {}).items():
        vertices[n].output[0].value = v

    for n in circuit['refer_by_name']:
        vertices[n].refer_by_name = True
    return list(vertices.values())

def check_vertex(v):
    tp, n = v.type, v.name

    input = [n for (n, i) in zip(tp.input, v.input)]
    disc = tp.input[len(input):]
    fmt = 'Vertex %s has disconnected inputs: %s'
    if disc:
        raise ValueError(fmt % (n, ', '.join(disc)))

    fmt = 'Constant %s has no value'
    if tp.name == 'const' and v.output[0].value is None:
        raise ValueError(fmt % n)

    if not v.type.optional_outputs:
        fmt = 'Vertex %s has disconnected outputs: %s'
        outs = [n for (n, wire) in zip(v.type.output, v.output)
                if not wire.destinations]
        if outs:
            raise ValueError(fmt % (n, ', '.join(outs)))

    fmt = 'Vertex %s has superfluous inputs: %s'
    extra = input[len(tp.input):]
    if extra:
        raise ValueError(fmt % (n, ', '.join(extra)))

def main():
    circuit_path, test_path = [Path(p) for p in argv[1:]]
    circuit_name = circuit_path.stem

    vertices = load_circuit(circuit_path)

    for v in vertices:
        check_vertex(v)

    infer_vertices(vertices)

    OUTPUT.mkdir(exist_ok = True)
    render_module(vertices, circuit_name, OUTPUT)

    tests = load_json(test_path)
    shuffle(tests)
    render_tb(vertices, tests, circuit_name, OUTPUT)

    path = OUTPUT / f'{circuit_name}.png'
    plot_vertices(vertices, path,
                  False, False, True,
                  False, False)
    path = OUTPUT / f'{circuit_name}_statements.png'
    plot_expressions(vertices, path, False, True)

main()
