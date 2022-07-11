from collections import defaultdict
from itertools import groupby, product
from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template
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

tp_to_binop = {
    'and' : '&',
    'xor' : '^',
    'or' : '|',
    'ge' : '>',
    'eq' : '==',
    'sub' : '-',
    'add' : '+'
}

WIRE_OWNERS = {'mux2', 'input', 'output', 'flip-flop'}
OUTPUT = Path('output')

def render_lval(lval_tp, tp, name, arity):
    arity = f'[{arity-1}:0]'
    return f'{lval_tp} {arity} {name}'

def render_rval(V, pred, n, outer):
    tp, ar = V[n]
    is_binop = tp in tp_to_binop
    r_args = []
    for n2 in pred.get(n, []):
        r_arg = n2
        if not V[n2][0] in WIRE_OWNERS:
            r_arg = render_rval(V, pred, n2, outer and not is_binop)
        r_args.append(r_arg)
    if tp.startswith('const_'):
        return tp[6:]
    elif is_binop:
        binop = tp_to_binop[tp]
        s = f'{r_args[0]} {binop} {r_args[1]}'
        if not outer:
            s = f'({s})'
        return s
    elif tp == 'not':
        return '!' + r_args[0]
    elif tp == 'mux2':
        return '%s\n        ? %s\n        : %s' % tuple(r_args)
    elif tp == 'cat':
        return '{%s, %s}' % tuple(r_args)
    elif tp == 'slice':
        return '%s[%s:%s]' % tuple(r_args)
    elif tp in ('input', 'flip-flop'):
        return n
    elif tp == 'output':
        return r_args[0]
    assert False

ENV.globals.update(zip = zip,
                   render_rval = render_rval,
                   render_lval = render_lval)

def input_nodes(V):
    ins = [(n, ar) for n, (tp, ar) in V.items() if tp == 'input']
    return sorted(ins)

def output_nodes(V):
    outs = [(n, ar) for n, (tp, ar) in V.items() if tp == 'output']
    return sorted(outs)

def sort_groupby(seq, keyfun, valfun):
    d = defaultdict(set)
    for el in seq:
        d[keyfun(el)].add(valfun(el))
    return [(k, sorted(v)) for k, v in sorted(d.items())]

def render_verilog(V, E, pred, mod_name, dir):
    keyfun, elfun = lambda x: x[1], lambda x: x[0]
    ins = input_nodes(V)
    gr_ins = sort_groupby(ins, keyfun, elfun)

    outs = output_nodes(V)
    gr_outs = sort_groupby(outs, keyfun, elfun)

    inouts = ins + outs
    inouts = [n for (n, ar) in inouts]

    ffs_per_clk = defaultdict(set)
    for ff, (tp, ar) in V.items():
        if tp == 'flip-flop':
            clk, wire = pred[ff]
            ffs_per_clk[clk].add((ff, wire, ar))

    ffs = [((n, ar),
            sorted([f for (f, t, pf, pt) in E if t == n]))
           for n, (tp, ar) in V.items()
           if tp == 'flip-flop'
    ]

    internal_wires = [(n, tp, ar) for (n, (tp, ar)) in V.items()
                      if tp not in ('input', 'output', 'flip-flop')]
    output_wires = [(n, tp, ar) for (n, (tp, ar)) in V.items()
                    if tp == 'output']

    kwargs = {
        'inouts' : inouts,
        'gr_ins' : gr_ins,
        'gr_outs' : gr_outs,

        'internal_wires' :  internal_wires,
        'output_wires' : output_wires,

        'pred' : pred,
        'V' : V,

        'ffs' : ffs,
        'ffs_per_clk' : ffs_per_clk,
        'mod_name' : mod_name,
        'WIRE_OWNERS' : WIRE_OWNERS
    }
    render_tmpl_to_file('module.v', dir / f'{mod_name}.v', **kwargs)

def render_verilog_tb(V, E, tests, mod_name, clk_n_rstn, dir):
    def fmt_arity(n, ar):
        size = max(5, len(n))
        ind = 'b' if ar == 1  else 'd'
        return f'%{size}{ind}'

    keyfun, elfun = lambda x: x[1], lambda x: x[0]
    ins = input_nodes(V)
    gr_ins = sort_groupby(ins, keyfun, elfun)

    outs = output_nodes(V)
    gr_outs = sort_groupby(outs, keyfun, elfun)
    inouts = ins + outs

    value_fmts = [fmt_arity(*io) for io in inouts]
    header_fmts = ['%5s' for _ in inouts]
    names = [n for (n, ar) in inouts]
    quoted_names = [f'"{n}"' for n in names]


    ranges = [list(range(2**ar)) for (_, ar) in ins]
    assignments = list(product(*ranges))
    kw = {
        'mod_name' : mod_name,
        'tests' : tests,

        'ins' : ins,
        'outs' : outs,
        'gr_ins' : gr_ins,
        'gr_outs' : gr_outs,

        'value_fmts' : value_fmts,
        'header_fmts' : header_fmts,
        'names' : names,
        'quoted_names' : quoted_names,

        # Assignments
        'assignments' : assignments,

        # Special signals
        'clk_n_rstn' : clk_n_rstn,

        # Rendering functions
        'render_lval' : render_lval
    }
    render_tmpl_to_file('tb.v', dir / f'{mod_name}_tb.v', **kw)

def style_node(n, tp, ar):
    shape = 'box'
    label = n
    width = height = 0.55
    color = 'black'
    fillcolor = 'white'
    if tp.startswith('const'):
        shape = 'box'
        width = height = 0.3
        val = tp.replace('const_', '')
        label = f'{val}[{ar}]'
    elif tp in tp_to_binop:
        label = tp_to_binop[tp]
    elif tp == 'slice':
        label = 'slice'
    elif tp == 'not':
        label = '!'
    elif tp in ('input', 'output'):
        shape = 'oval'
        label = f'{n}[{ar}]'
    elif tp == 'mux2':
        shape = 'diamond'
        label = tp
    elif tp == 'flip-flop':
        label = f'{n}[{ar}]'
        fillcolor = '#ffffdd'

    return {'shape' : shape,
            'label' : label,
            'width' : width,
            'height' : height,
            'color' : color,
            'fillcolor' : fillcolor}

def style_edge(n1, tp1, ar1, n2, tp2, ar2, pf, pt):
    color = 'black'
    style = 'solid'
    penwidth = 0.5
    if tp2 == 'mux2':
        if pt == 1:
            color = '#00aa00'
        elif pt == 2:
            color = '#aa0000'
    elif tp2 == 'mux2_2':
        if pt in (1, 2):
            color = '#00aa00'
        elif pt in (3, 4):
            color = '#aa0000'
    elif tp2 == 'flip-flop':
        if pt == 0:
            style = 'dashed'
    if ar1 != 1:
        penwidth = 1.0
    return {
        'color' : color,
        'style' : style,
        'penwidth' : penwidth
        }

def plot_hw_graph(V, E, mod_name, draw_clk, dir):
    G = AGraph(strict = False, directed = True)
    graph_attrs = {
        'dpi' : 300,
        'ranksep' : 0.4,
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

    for n, (tp, ar) in V.items():
        attrs = style_node(n, tp, ar)
        print('name', n)
        if n != 'clk' or draw_clk:
            G.add_node(n, **attrs)

    for n1, n2, pf, pt in E:
        (tp1, ar1), (tp2, ar2) = V[n1], V[n2]
        attrs = style_edge(n1, tp1, ar1, n2, tp2, ar2, pf, pt)
        if n1 != 'clk' or draw_clk:
            G.add_edge(n1, n2, **attrs)

    G.draw(dir / f'{mod_name}.png', prog='dot')

def main():
    V = {
        'clk' : ('input', 1),
        'rstn' : ('input', 1),
        'a' : ('input', 8),
        'b' : ('input', 8),
        'in_valid' : ('input', 1),

        'in_ready' : ('output', 1),
        'out_valid' : ('output', 1),
        'o' : ('output', 8),

        'c0_1' : ('const_0', 1),
        'c0_8' : ('const_0', 8),
        'c7_8' : ('const_7', 8),
        'c8_8' : ('const_8', 8),
        'c15_8' : ('const_15', 8),

        'begin_p' : ('and', 1),
        'continue_p' : ('or', 1),

        'not_p' : ('not', 1),
        'not_rstn' : ('not', 1),

        'x_ge_y' : ('ge', 1),
        'y_eq_0' : ('eq', 1),
        'y_sub_x' : ('sub', 8),

        'y_eq_0_and_p' : ('and', 1),
        'p_next' : ('mux2', 1),

        'next' : ('mux2', 16),
        'next2' : ('mux2', 16),
        'next3' : ('mux2', 16),

        'p' : ('flip-flop', 1),
        'xy' : ('flip-flop', 16),

        'cat_ab' : ('cat', 16),
        'cat_yx' : ('cat', 16),
        'cat_x_y_sub_x' : ('cat', 16),

        'sl_y_fr_xy' : ('slice', 8),
        'sl_x_fr_xy' : ('slice', 8)
    }
    E = {

        # Slicing
        ('xy', 'sl_y_fr_xy', 0, 0),
        ('c7_8', 'sl_y_fr_xy', 0, 1),
        ('c0_8', 'sl_y_fr_xy', 0, 2),

        ('xy', 'sl_x_fr_xy', 0, 0),
        ('c15_8', 'sl_x_fr_xy', 0, 1),
        ('c8_8', 'sl_x_fr_xy', 0, 2),

        # Clock connections
        ('clk', 'p', 0, 0),
        ('clk', 'xy', 0, 0),

        # Connect registers
        ('p_next', 'p', 0, 1),
        ('next', 'xy', 0, 1),
        # ('x_next', 'x', 0, 1),
        # ('y_next', 'y', 0, 1),

        # Concatenate
        ('sl_y_fr_xy', 'cat_yx', 0, 0),
        ('sl_x_fr_xy', 'cat_yx', 0, 1),
        # ('x', 'cat_xy', 0, 0),
        # ('y', 'cat_xy', 0, 1),
        ('a', 'cat_ab', 0, 0),
        ('b', 'cat_ab', 0, 1),

        ('sl_x_fr_xy', 'cat_x_y_sub_x', 0, 0),
        ('y_sub_x', 'cat_x_y_sub_x', 0, 1),

        # not_p
        ('p', 'not_p', 0, 0),

        # not_p
        ('rstn', 'not_rstn', 0, 0),

        # begin_p
        ('in_valid', 'begin_p', 0, 0),
        ('not_p', 'begin_p', 0, 1),

        # continue_p
        ('p', 'continue_p', 0, 0),
        ('in_valid', 'continue_p', 0, 0),

        # x_ge_y
        ('sl_x_fr_xy', 'x_ge_y', 0, 0),
        ('sl_y_fr_xy', 'x_ge_y', 0, 1),

        # y_eq_0
        ('sl_y_fr_xy', 'y_eq_0', 0, 0),
        ('c0_8', 'y_eq_0', 0, 1),

        # y_sub_x
        ('sl_y_fr_xy', 'y_sub_x', 0, 0),
        ('sl_x_fr_xy', 'y_sub_x', 0, 1),

        # next
        ('begin_p', 'next', 0, 0),
        ('cat_ab', 'next', 0, 1),
        ('next2', 'next', 0, 2),

        # next3
        ('x_ge_y', 'next3', 0, 0),
        ('cat_yx', 'next3', 0, 1),
        ('cat_x_y_sub_x', 'next3', 0, 2),

        # next2
        ('p', 'next2', 0, 0),
        ('next3', 'next2', 0, 1),
        ('xy', 'next2', 0, 2),

        # next
        ('begin_p', 'next', 0, 0),
        ('cat_ab', 'next', 0, 1),
        ('next2', 'next', 0, 2),

        # Connect next muxes
        ('not_rstn', 'p_next', 0, 0),
        ('c0_1', 'p_next', 0, 1),
        ('continue_p', 'p_next', 0, 2),

        # Stuff for p
        ('not_p', 'in_ready', 0, 0),

        # Other stuff
        ('y_eq_0', 'y_eq_0_and_p', 0, 0),
        ('p', 'y_eq_0_and_p', 0, 1),
        ('y_eq_0_and_p', 'out_valid', 0, 0),
        ('sl_x_fr_xy', 'o', 0, 0)
    }

    # Create pred and succ
    succ = defaultdict(set)
    pred = defaultdict(set)
    for v1, v2, pf, pt in E:
        succ[v1].add((pf, v2))
        pred[v2].add((pt, v1))

    pred = {k : [v2 for _, v2 in sorted(v)]
            for (k, v) in pred.items()}
    OUTPUT.mkdir(exist_ok = True)


    tests = [
        {
            'name' : 'Ready after reset',
            'setup' : [
                ({
                    'rstn' : 0
                }, 1)
            ],
            'post' : {'in_ready' : 1},
        },
        {
            'name' : 'Propagate a to o',
            'setup' : [
                ({
                    'rstn' : 0
                }, 1),
                ({
                    'rstn' : 1,
                    'in_valid' : 1,
                    'a' : 5,
                    'b' : 2
                }, 1)
            ],
            'post' : {'o' : 5}
        },
        {
            'name' : 'Read only one tick',
            'setup' : [
                ({
                    'rstn' : 0
                }, 1),
                ({
                    'rstn' : 1,
                    'in_valid' : 1,
                    'a' : 5,
                    'b' : 2
                }, 1),
                ({
                    'a' : 22
                }, 1)
            ],
            'post' : {'o' : 2}
        }
    ]
    shuffle(tests)

    render_verilog(V, E, pred, 'test01', OUTPUT)
    render_verilog_tb(V, E, tests, 'test01', ('clk', 'rstn'), OUTPUT)
    plot_hw_graph(V, E, 'test01', False, OUTPUT)



main()
