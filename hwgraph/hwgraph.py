# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from collections import defaultdict
from itertools import groupby, product
from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template
from json import loads
from pathlib import Path
from pygraphviz import AGraph
from random import shuffle

TMPL_PATH = Path(__file__).parent / 'templates'
ENV = Environment(loader = FileSystemLoader(TMPL_PATH),
                  undefined = StrictUndefined)
def render_tmpl_to_file(tmpl_name, file_path, **kwargs):
    tmpl = ENV.get_template(tmpl_name)
    txt = tmpl.render(**kwargs)
    with open(file_path, 'wt') as of:
        of.write(txt + '\n')

class Vertex:
    def __init__(self, name, type, arity):
        self.name = name
        self.type = type
        self.arity = arity
        self.predecessors = []

        # We don't yet support vertices with multiple outputs.
        self.successors  = set()

    def __repr__(self):
        return 'Vertex<%s:%s:%s>' % (self.name, self.type, self.arity or '?')

DEFAULT_INT_ARITY = 20
BINARY_OPS = {'and', 'xor', 'or', 'ge', 'eq', 'sub', 'add'}

UNARY_OPS = {'not'}
COMPARE_OPS = {'ge', 'eq'}
ARITH_OPS = {'and', 'xor', 'or', 'sub', 'add'}
TP_TO_SYMBOL = {
    'and' : '&',
    'xor' : '^',
    'or' : '|',
    'ge' : '>',
    'eq' : '==',
    'sub' : '-',
    'add' : '+',
    'not' : '!'
}

WIRE_OWNERS = {'if', 'input', 'output', 'reg'}
OUTPUT = Path('output')

def render_lval(lval_tp, v):
    return f'{lval_tp} [{v.arity - 1}:0] {v.name}'

def render_rval(v1, outer):
    r_args = []
    tp = v1.type
    is_binop = tp in BINARY_OPS
    for v2 in v1.predecessors:
        r_arg = v2.name
        if not v2.type in WIRE_OWNERS:
            r_arg = render_rval(v2, outer and not is_binop)
        r_args.append(r_arg)
    if tp.startswith('const_'):
        return tp[6:]
    elif tp == 'if':
        return '%s\n        ? %s\n        : %s' % tuple(r_args)
    elif tp == 'cat':
        return '{%s, %s}' % tuple(r_args)
    elif tp == 'slice':
        return '%s[%s:%s]' % tuple(r_args)
    elif is_binop:
        binop = TP_TO_SYMBOL[tp]
        s = f'{r_args[0]} {binop} {r_args[1]}'
        if not outer:
            s = f'({s})'
        return s
    elif tp == 'not':
        return TP_TO_SYMBOL[tp] + r_args[0]
    elif tp in ('input', 'reg'):
        return n
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
    return sorted([(k, list(v)) for k, v in grps])

def render_verilog(vertices, mod_name, path):
    ins = [v for v in vertices if v.type == 'input']
    outs = [v for v in vertices if v.type == 'output']
    inouts = ins + outs

    keyfun = lambda v: v.arity
    gr_ins = groupby_sort(ins, keyfun)
    gr_outs = groupby_sort(outs, keyfun)
    io_groups = [('input', gr_ins), ('output', gr_outs)]

    # Group registers by driving clock.
    regs = [v for v in vertices if v.type == 'reg']
    regs_per_clk = groupby_sort(regs, lambda v: v.predecessors[0].name)

    internal_wires = [v for v in vertices
                      if v.type not in {'input', 'output', 'reg'}]

    output_wires = [v for v in vertices if v.type == 'output']

    kwargs = {
        'inouts' : inouts,
        'io_groups' : io_groups,
        'internal_wires' :  internal_wires,
        'output_wires' : output_wires,
        'regs_per_clk' : regs_per_clk,
        'mod_name' : mod_name,
        'WIRE_OWNERS' : WIRE_OWNERS
    }
    render_tmpl_to_file('module.v', path / f'{mod_name}.v', **kwargs)

def render_verilog_tb(vertices, tests, mod_name, clk, rstn, dir):
    ins = [v for v in vertices if v.type == 'input']
    outs = [v for v in vertices if v.type == 'output']
    inouts = ins + outs

    keyfun = lambda v: v.arity
    gr_ins = groupby_sort(ins, keyfun)
    gr_outs = groupby_sort(outs, keyfun)
    io_groups = [('reg', gr_ins), ('wire', gr_outs)]

    def fmt_arity(v):
        size = max(5, len(v.name))
        ind = 'b' if v.arity == 1 else 'd'
        return f'%{size}{ind}'
    monitor_verts = [Vertex('cycle', None, DEFAULT_INT_ARITY)] \
        + [v for v in inouts if v.name not in clk]

    monitor_fmt = ' '.join(fmt_arity(v) for v in monitor_verts)
    monitor_args = ', '.join(v.name for v in monitor_verts)

    display_fmt = ' '.join('%5s' for _ in monitor_verts)
    display_args = ', '.join(f'"{v.name}"' for v in monitor_verts)

    kw = {
        'mod_name' : mod_name,
        'tests' : tests,
        'io_groups' : io_groups,
        'inouts' : inouts,

        'display_fmt' : display_fmt,
        'display_args' : display_args,
        'monitor_fmt' : monitor_fmt,
        'monitor_args' : monitor_args,

        'clk' : clk,
        'rstn' : rstn
    }
    render_tmpl_to_file('tb.v', dir / f'{mod_name}_tb.v', **kw)

def style_node(v):
    n, tp = v.name, v.type
    ar = v.arity or '?'

    shape = 'box'
    width = height = 0.55
    color = 'black'
    fillcolor = 'white'
    if tp.startswith('const'):
        shape = 'box'
        width = height = 0.3
        val = tp.replace('const_', '')
        label = f'{val}:{ar}'
    elif tp in TP_TO_SYMBOL:
        label = f'{TP_TO_SYMBOL[tp]}:{ar}'
    elif tp in ('input', 'output'):
        shape = 'oval'
        label = f'{n}:{ar}'
        fillcolor = '#ffcccc' if tp == 'input' else '#bbccff'
    elif tp == 'if':
        shape = 'diamond'
        label = f'{tp}:{ar}'
    elif tp == 'reg':
        label = f'{n}:{ar}'
        fillcolor = '#ffffdd'
    elif tp in ('cat', 'slice'):
        label = f'{tp}:{ar}'
    else:
        label = n

    return {'shape' : shape,
            'label' : label,
            'width' : width,
            'height' : height,
            'color' : color,
            'fillcolor' : fillcolor}

def style_edge(pt, v1, v2):
    color = 'black'
    style = 'solid'
    penwidth = 0.5
    if v2.type == 'if':
        if pt == 1:
            color = 'black;0.9999:#00aa00'
        elif pt == 2:
            color = 'black;0.9999:#aa0000'
    elif v2.type == 'reg':
        if pt == 0:
            style = 'dashed'
    if v1.arity != 1:
        penwidth = 1.0
    return {
        'color' : color,
        'style' : style,
        'penwidth' : penwidth
        }

def plot_hw_graph(vertices, mod_name, draw_clk, path):
    G = AGraph(strict = False, directed = True)
    graph_attrs = {
        'dpi' : 300,
        'ranksep' : 0.3,
        'fontname' : 'Inconsolata',
        'bgcolor' : 'transparent',
        'rainkdir' : 'LR'
    }
    G.graph_attr.update(graph_attrs)
    node_attrs = {
        'shape' : 'box',
        'width' : 0.55,
        'style' : 'filled',
        'fillcolor' : 'white'
    }
    G.node_attr.update(node_attrs)
    edge_attrs = {
        'fontsize' : '10pt'
    }
    G.edge_attr.update(edge_attrs)

    for v in vertices:
        if v.name != 'clk' or draw_clk:
            attrs = style_node(v)
            G.add_node(v.name, **attrs)

    for v2 in vertices:
        for i, v1 in enumerate(v2.predecessors):
            if v1.name != 'clk' or draw_clk:
                attrs = style_edge(i, v1, v2)
                G.add_edge(v1.name, v2.name, **attrs)
    G.draw(path / f'{mod_name}.png', prog='dot')

def infer_arity_fwd(v):
    if v.arity:
        return False
    ps = [p for p in v.predecessors]
    arities = [p.arity for p in ps]
    if v.type in {'if', 'reg'}:
        arities = arities[1:]
        ps = ps[1:]
    if v.type == 'cat':
        if all(arities):
            v.arity = sum(arities)
            return True
    elif v.type == 'slice':
        hi = int(ps[1].type[6:])
        lo = int(ps[2].type[6:])
        v.arity = hi - lo + 1
        return True
    elif v.type in {'if', 'reg'} | ARITH_OPS | UNARY_OPS:
        if len(set(arities)) == 1 and arities[0]:
            v.arity = arities[0]
            return True
    elif v.type in COMPARE_OPS:
        v.arity = 1
        return True
    return False

def assert_arity(v, arity):
    if v.arity == arity:
        return False
    elif v.arity is None:
        v.arity = arity
        return True
    print("%s incompatible with arity %d." % (v, arity))
    print('Preds/succs: %s' % (v.predecessors, v.successors))
    assert False

def infer_arity_bwd(v):
    data_ps = [p for p in v.predecessors]
    if v.type in {'if', 'reg', 'slice'}:
        data_ps = data_ps[1:]
    if v.type in {'output'} | UNARY_OPS:
        return assert_arity(data_ps[0], v.arity)
    if v.type in BINARY_OPS | {'if', 'slice'}:
        v1, v2 = data_ps
        ar1, ar2 = v1.arity, v2.arity
        changed = False
        if ar1:
            changed = assert_arity(v2, ar1)
        if ar2:
            changed = changed or assert_arity(v1, ar2)
        if v.type == 'slice':
            for vp in [v1, v2]:
                if len(vp.successors) == 1 and not vp.arity:
                    vp.arity = DEFAULT_INT_ARITY
                    changed = True
        return changed
    return False


def infer_arities(vertices):
    print({'if', 'reg'} | ARITH_OPS | UNARY_OPS)
    changed = True
    while changed:
        changed = False
        for v in vertices:
            changed = changed or infer_arity_fwd(v)
        for v in vertices:
            changed = changed or infer_arity_bwd(v)

def main():
    circuit = load_json('examples/gcd.json')
    vertices = {}
    for tp, ns in circuit['types'].items():
        for n in ns:
            vertices[n] = Vertex(n, None, None)
            vertices[n].type = tp
    for ar, ns in circuit['arities'].items():
        ar = int(ar)
        for n in ns:
            vertices[n].arity = ar
    for n, ps in circuit['predecessors'].items():
        ps = [vertices[p] for p in ps]
        v = vertices[n]
        v.predecessors = ps
        for p in ps:
            p.successors.add(v)

    vertices = sorted(vertices.values(),
                      key = lambda v: (v.type, v.arity, v.name))
    infer_arities(vertices)

    OUTPUT.mkdir(exist_ok = True)

    render_verilog(vertices, 'test01', OUTPUT)

    tests = load_json('examples/gcd_tb.json')
    shuffle(tests)
    render_verilog_tb(vertices, tests, 'test01', 'clk', 'rstn', OUTPUT)
    plot_hw_graph(vertices, 'test01', False, OUTPUT)

main()
