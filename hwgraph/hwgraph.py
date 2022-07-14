# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from collections import defaultdict
from html import escape
from itertools import groupby, product
from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template
from json import loads
from more_itertools import partition
from pathlib import Path
from pygraphviz import AGraph
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

class Vertex:
    def __init__(self, name, type, arity, value):
        self.name = name
        self.type = type
        self.arity = arity
        self.predecessors = []
        self.value = value
        self.alias = None

        # We don't yet support vertices with multiple outputs.
        self.successors = []
        self.internalized = {}

    def __repr__(self):
        return 'Vertex<%s:%s:%s>' % (self.name, self.type, self.arity or '?')

def clone_vertex(v1):
    v2 = Vertex(v1.name, v1.type, v1.arity, v1.value)
    v2.internalized = v1.internalized
    return v2

def replace_vertex_pred(v, old, new):
    idx = v.predecessors.index(old)
    v.predecessors[idx] = new
    new.successors.append(v)

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

INTERNALIZABLE_TYPES = {'cat', 'const', 'input'} | BINARY_OPS | UNARY_OPS

WIRE_OWNERS = {'if', 'input', 'output', 'reg'}
OUTPUT = Path('output')

def render_lval(lval_tp, v):
    return f'{lval_tp} [{v.arity - 1}:0] {v.name}'

def render_rval(v1, parent_tp):
    r_args = []
    tp = v1.type
    for v2 in v1.predecessors:
        r_arg = v2.name
        if not v2.type in WIRE_OWNERS:
            r_arg = render_rval(v2, tp)
        r_args.append(r_arg)
    if tp == 'const':
        if parent_tp == 'cat':
            return f"{v1.arity}'b{v1.value}"
        return f'{v1.value}'
    elif tp == 'if':
        return '%s\n        ? %s\n        : %s' % tuple(r_args)
    elif tp == 'cat':
        return '{%s}' % ', '.join(r_args)
    elif tp == 'slice':
        return '%s[%s:%s]' % tuple(r_args)
    elif tp in BINARY_OPS:
        binop = TP_TO_SYMBOL[tp]
        s = f'{r_args[0]} {binop} {r_args[1]}'
        if parent_tp in BINARY_OPS:
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
        None : 37
    }
    fmts = [ansi_escape(fmt_arity(v, ind), 1, colors[v.type])
            for v in vs]
    return ' '.join(fmts)

def render_args(vs, quote):
    args = [['27', f'"{v.name}"' if quote else v.name, '27']
            for v in vs]
    args = flatten(args)
    return ', '.join(args)

def render_verilog_tb(vertices, tests, mod_name, path):
    ins = [v for v in vertices if v.type == 'input']
    outs = [v for v in vertices if v.type == 'output']
    inouts = ins + outs

    keyfun = lambda v: v.arity
    gr_ins = groupby_sort(ins, keyfun)
    gr_outs = groupby_sort(outs, keyfun)
    io_groups = [('reg', gr_ins), ('wire', gr_outs)]

    inouts_no_clk, inouts_clk = partition(lambda v: v.name == 'clk', inouts)

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

def colorize(s, col):
    return '<font color="%s">%s</font>' % (col, s)

def render_label(v, parent_tp):
    tp = v.type
    preds = v.predecessors
    interns = v.internalized
    if parent_tp and v.alias:
        return colorize(v.alias, '#6ca471')
    elif tp == 'slice':
        if interns:
            return f'[{interns[1].value}:{interns[2].value}]'
        return tp
    elif tp == 'const':
        return f'{v.value}'
    elif tp == 'reg':
        return v.name
    elif tp == 'input':
        return colorize(v.name, '#aa8888')
    elif tp == 'output':
        return colorize(v.name, '#7788aa')
    elif tp in UNARY_OPS:
        sym = escape(TP_TO_SYMBOL[tp])
        if interns:
            x = render_label(interns[0], tp)
            return f'{sym}{x}'
        return sym
    elif tp in BINARY_OPS:
        sym = escape(TP_TO_SYMBOL[tp])
        if not interns:
            return sym
        l, r = '**'
        if 0 in interns:
            l = render_label(interns[0], tp)
        if  1 in interns:
            r = render_label(interns[1], tp)
        s = f'{l} {sym} {r}'
        if parent_tp in BINARY_OPS:
            s = f'({s})'
        return s
    elif tp == 'if':
        if interns:
            cond, l, r = '***'
            if 0 in interns:
                cond = render_label(interns[0], tp)
            if 1 in interns:
                l = render_label(interns[1], tp)
            if 2 in interns:
                r = render_label(interns[2], True)
            return f'{cond} ? {l} : {r}'
        return tp
    elif tp == 'cat':
        if interns:
            parts = ['*'] * len(preds)
            for i, v2 in interns.items():
                parts[i] = render_label(v2, tp)
            return "{%s}" % ', '.join(parts)
        return tp
    else:
        assert False
    return label

def style_node(v, draw_arities):
    n, tp = v.name, v.type

    shape = 'box'
    width = height = 0.55
    color = 'black'
    fillcolor = 'white'

    label = render_label(v, None)
    if tp == 'const':
        shape = 'box'
        width = height = 0.3
    elif tp in ('input', 'output'):
        shape = 'oval'
        fillcolor = '#ffcccc' if tp == 'input' else '#bbccff'
    elif tp == 'if':
        shape = 'diamond'
    elif tp == 'reg':
        fillcolor = '#ffffdd'

    if v.alias:
        var = colorize(v.alias, '#6ca471')
        label = f'{var} &larr; {label}'

    if draw_arities:
        label = f'{label}:{v.arity or "?"}'

    return {'shape' : shape,
            'label' : f'<{label}>',
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

def setup_graph():
    G = AGraph(strict = False, directed = True)
    graph_attrs = {
        'dpi' : 300,
        'ranksep' : 0.3,
        'fontname' : 'Inconsolata',
        'bgcolor' : 'transparent'
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
    return G


def plot_vertices(vertices, png_path, draw_clk, draw_arities):
    G = setup_graph()

    # Vertices names are not always unique.
    ids = {v : i for i, v in enumerate(vertices)}

    for v in vertices:
        if v.name != 'clk' or draw_clk:
            attrs = style_node(v, draw_arities)
            G.add_node(ids[v], **attrs)

    for v2 in vertices:
        for i, v1 in enumerate(v2.predecessors):
            if v1 and v1.name != 'clk' or draw_clk:
                attrs = style_edge(i, v1, v2)
                G.add_edge(ids[v1], ids[v2], **attrs)
    G.draw(png_path, prog='dot')

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
        hi = int(ps[1].value)
        lo = int(ps[2].value)
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
    data_ps = v.predecessors
    tp = v.type
    arity = v.arity
    if tp in {'if', 'reg', 'slice'}:
        data_ps = data_ps[1:]
    if tp in {'output'} | UNARY_OPS:
        return assert_arity(data_ps[0], arity)
    if tp in BINARY_OPS | {'if', 'slice'}:
        v1, v2 = data_ps
        ar1, ar2 = v1.arity, v2.arity
        changed = False
        if ar1:
            changed = assert_arity(v2, ar1)
        if ar2:
            changed = changed or assert_arity(v1, ar2)
        if v.type == 'slice':
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

def clone_simple_vertices(vertices):
    # Duplicate constant nodes
    clones = []
    for v1 in vertices:
        tp = v1.type
        if any(v1.predecessors):
            continue
        if tp in {'eq', 'const', 'input'} | UNARY_OPS | BINARY_OPS:
            hd, tl = v1.successors[0], v1.successors[1:]
            if tl:
                for v2 in tl:
                    v1p = clone_vertex(v1)
                    replace_vertex_pred(v2, v1, v1p)
                    clones.append(v1p)
            v1.successors = [hd]
    return clones

def internalize_vertices(vertices):
    changed = True
    while changed:
        changed = False
        vertices.extend(clone_simple_vertices(vertices))

        all_removed = []
        for v in vertices:
            removed = []
            tp = v.type
            if tp in {'cat', 'slice', 'if'} | BINARY_OPS | UNARY_OPS:
                for i, p in enumerate(list(v.predecessors)):
                    if (p and
                        p.type in INTERNALIZABLE_TYPES and
                        not any(p.predecessors) and
                        len(set(p.successors)) == 1):
                        v.internalized[i] = p
                        v.predecessors[i] = None
                        removed.append(p)
                        changed = True
                    if p and p.alias:
                        v.internalized[i] = p
                        v.predecessors[i] = None
                        p.successors.remove(v)

            all_removed.extend(removed)
        vertices = [v for v in vertices if v not in all_removed]
    return vertices

def main():
    circuit_file, test_file = argv[1:]
    circuit = load_json(circuit_file)
    vertices = {}
    for tp, ns in circuit['types'].items():
        for n in ns:
            vertices[n] = Vertex(n, None, None, None)
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
            p.successors.append(v)
    for n, v in circuit['values'].items():
        vertices[n].value = v

    for n, v in circuit['aliases'].items():
        vertices[n].alias = v

    vertices = sorted(vertices.values(),
                      key = lambda v: (v.type, v.arity, v.name))
    infer_arities(vertices)

    for v in vertices:
        if not v.arity:
            print(v)
            print(v.successors)
        assert v.arity

    OUTPUT.mkdir(exist_ok = True)
    render_verilog(vertices, 'test01', OUTPUT)

    tests = load_json(test_file)
    shuffle(tests)

    render_verilog_tb(vertices, tests, 'test01', OUTPUT)

    #vertices = internalize_vertices(vertices)
    plot_vertices(vertices, OUTPUT / 'test01.png', False, False)

main()
