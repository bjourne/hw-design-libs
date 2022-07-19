# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from collections import defaultdict
from hwgraph import (UNARY_OPS,
                     BINARY_OPS, BALANCED_BINARY_OPS,
                     TYPE_TO_SYMBOL,
                     Vertex,
                     package_vertex)
from hwgraph.plotting import plot_vertices, plot_expressions
from itertools import groupby, product
from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template
from json import loads
from more_itertools import partition
from pathlib import Path
from random import shuffle
from sys import argv

TMPL_PATH = Path(__file__).parent / 'templates'
ENV = Environment(loader = FileSystemLoader(TMPL_PATH),
                  undefined = StrictUndefined)
def render_tmpl_to_file(tmpl_name, file_path, **kwargs):
    tmpl = ENV.get_template(tmpl_name)
    txt = tmpl.render(**kwargs)
    with open(file_path, 'wt') as of:
        of.write(txt + '\n')

DEFAULT_INT_ARITY = 20
COMPARE_OPS = {'ge', 'gt', 'eq'}
ARITH_OPS = {'and', 'xor', 'or', 'sub', 'add'}

OUTPUT = Path('output')

def render_lval(lval_tp, v):
    return f'{lval_tp} [{v.arity - 1}:0] {v.name}'

def render_rval_const(parent, child):
    # Putting arity declarations on every constant is ugly so we only
    # do it when it is (probably) necessary.
    if (child.type.name in BINARY_OPS and
        any(s.type.name == 'cat' for s in child.successors) or
        child.type.name == 'cat'):
        return "%s'd%s" % (parent.arity, parent.value)
    return str(parent.value)

def render_rval(v1, parent):
    def render_rval_pred(child, parent):
        if (child.refer_by_name or
            child.type.name == 'if' or
            any(v2.type.name == 'slice' and
                v2.predecessors.index(child) == 0
                for v2 in child.successors)):
            return child.name
        return render_rval(child, parent)
    tp = v1.type.name
    sym = TYPE_TO_SYMBOL.get(tp)

    r_args = [render_rval_pred(v2, v1) for v2 in v1.predecessors]
    r_args = tuple(r_args)
    if tp == 'const':
        return render_rval_const(v1, parent)
    elif tp == 'cast':
        return "%s'(%s)" % r_args
    elif tp == 'if':
        fmt = '%s ? %s : %s'
        if max(len(a) for a in r_args) > 14:
            fmt = '%s\n        ? %s\n        : %s'
        return fmt % r_args
    elif tp == 'cat':
        s = '%s, %s' % r_args
        return package_vertex(v1, parent) % s
    elif tp == 'slice':
        return '%s[%s:%s]' % r_args
    elif tp in BINARY_OPS:
        s = f'{r_args[0]} {sym} {r_args[1]}'
        return package_vertex(v1, parent) % s
    elif tp in UNARY_OPS:
        return f'{sym}{r_args[0]}'
    elif tp in {'input', 'reg'}:
        return v1.name
    elif tp == 'output':
        return r_args[0]
    assert False

ENV.globals.update(zip = zip,
                   render_rval = render_rval,
                   render_lval = render_lval)

def load_json(fname):
    # I like having comments in JSON.
    with open(fname, 'r') as f:
        lines = [l.strip() for l in f.readlines()]
        lines = [l for l in lines if not l.startswith('//')]
    return loads('\n'.join(lines))

def groupby_sort(seq, keyfun):
    grps = groupby(seq, keyfun)
    grps = [(k, list(v)) for k, v in grps]
    return sorted(grps)

def render_verilog(vertices, mod_name, path):
    vs_by_type = dict(groupby_sort(vertices, lambda v: v.type.name))

    keyfun = lambda v: v.arity
    gr_ins = groupby_sort(vs_by_type['input'], keyfun)
    gr_outs = groupby_sort(vs_by_type['output'], keyfun)
    io_groups = [('input', gr_ins), ('output', gr_outs)]

    # Group registers by driving clock.
    regs = vs_by_type['reg']
    regs_per_clk = groupby_sort(regs, lambda v: v.predecessors[0].name)

    others, regs = partition(lambda v: v.type.name == 'reg', vertices)
    others, explicit = partition(lambda v: v.refer_by_name, others)
    others, implicit = partition(lambda v: v.type.name == 'if', others)

    # Outputs
    outputs = vs_by_type['output']

    kwargs = {
        'inouts' : vs_by_type['input'] + vs_by_type['output'],
        'io_groups' : io_groups,
        'explicit' :  explicit,
        'implicit' : implicit,
        'outputs' : outputs,
        'regs_per_clk' : regs_per_clk,
        'mod_name' : mod_name,
    }
    render_tmpl_to_file('module.v', path / f'{mod_name}.v', **kwargs)

def fmt_arity(v, ind):
    size = max(5, len(v.name))
    if not ind:
        ind = 'b' if v.arity == 1 else 'd'
    return f'%{size}{ind}'

def ansi_escape(s, tp, col):
    return '%%c[%d;%dm' % (tp, col) + s + '%c[0m'

def flatten(seq):
    return [y for x in seq for y in x]

def render_fmts(vs, ind):
    colors = {
        'input' : 36,
        'output' : 33,
    }
    fmts = [ansi_escape(fmt_arity(v, ind), 1,
                        colors[v.type.name] if v.type else 37)
            for v in vs]
    return ' '.join(fmts)

def render_args(vs, quote):
    args = [['27', f'"{v.name}"' if quote else v.name, '27']
            for v in vs]
    args = flatten(args)
    return ', '.join(args)

def render_verilog_tb(vertices, tests, mod_name, path):
    vs_by_type = dict(groupby_sort(vertices, lambda v: v.type.name))

    ins = vs_by_type['input']
    outs = vs_by_type['output']
    inouts = ins + outs

    keyfun = lambda v: v.arity
    gr_ins = groupby_sort(ins, keyfun)
    gr_outs = groupby_sort(outs, keyfun)
    io_groups = [('reg', gr_ins), ('wire', gr_outs)]

    inouts_no_clk, inouts_clk = partition(lambda v: v.name == 'clk', inouts)

    # Monitoring setup.
    mon_verts = [Vertex('cycle', None, DEFAULT_INT_ARITY, 0)] \
        + list(inouts_no_clk)
    disp_fmt = render_fmts(mon_verts, 's')
    disp_args = render_args(mon_verts, True)
    mon_fmt = render_fmts(mon_verts, None)
    mon_args = render_args(mon_verts, False)

    kw = {
        'mod_name' : mod_name,
        'tests' : tests,
        'io_groups' : io_groups,
        'inouts' : inouts,
        'disp_fmt' : disp_fmt,
        'disp_args' : disp_args,
        'mon_fmt' : mon_fmt,
        'mon_args' : mon_args,
        'has_clk' : list(inouts_clk)
    }
    render_tmpl_to_file('tb.v', path / f'{mod_name}_tb.v', **kw)

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

class Type:
    def __init__(self, name, input, output):
        self.name = name
        self.input = input
        self.output = output

    def __repr__(self):
        fmt = '%s[(%s -> %s)]'
        args = self.name, ', '.join(self.input), ', '.join(self.output)
        return fmt % args

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
    for v in vertices:
        if not v.arity:
            print(v)
            print(v.successors)
        assert v.arity

    OUTPUT.mkdir(exist_ok = True)
    render_verilog(vertices, circuit_name, OUTPUT)

    tests = load_json(test_path)
    shuffle(tests)

    render_verilog_tb(vertices, tests, circuit_name, OUTPUT)

    path = OUTPUT / f'{circuit_name}.png'
    plot_vertices(vertices, path, False, False, True)

    path = OUTPUT / f'{circuit_name}_statements.png'
    plot_expressions(vertices, path)

main()
