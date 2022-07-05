from itertools import product
from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template
from pathlib import Path
from pygraphviz import AGraph

TMPL_PATH = Path(__file__).parent / 'templates'
ENV = Environment(loader = FileSystemLoader(TMPL_PATH),
                  undefined = StrictUndefined)
ENV.globals.update(zip = zip)

def render_tmpl_to_file(tmpl_name, file_path, **kwargs):
    tmpl = ENV.get_template(tmpl_name)
    txt = tmpl.render(**kwargs)
    with open(file_path, 'wt') as of:
        of.write(txt + '\n')

def render_lval(lval_tp, name, arity):
    print('rendering', name)
    arity = f'[{arity-1}:0]'
    return f'{lval_tp} {arity} {name}'


tp_to_binop = {
    'and' : '&',
    'xor' : '^',
    'or' : '|',
    'ge' : '>',
    'eq' : '==',
    'sub' : '-',
    'add' : '+'
}

def render_rval(tp, args):
    binop = tp_to_binop.get(tp)
    if binop:
        return f'{args[0][1]} {binop} {args[1][1]}'
    if tp == 'output':
        return args[0][1]
    elif tp == 'const_1':
        return '1'
    elif tp == 'const_0':
        return '0'
    elif tp == 'not':
        return '!' + args[0][1]
    elif tp == 'mux2':
        return '%s ? %s : %s' % (args[0][1], args[1][1], args[2][1])
    assert False

def input_nodes(V):
    ins = [(n, ar) for n, (tp, ar) in V.items() if tp == 'input']
    return sorted(ins)

def output_nodes(V):
    outs = [(n, ar) for n, (tp, ar) in V.items() if tp == 'output']
    return sorted(outs)

def render_verilog(V, E, mod_name):
    ins = input_nodes(V)
    outs = output_nodes(V)

    inouts = ins + outs
    inouts = [n for (n, ar) in inouts]

    ffs = [((n, ar),
            sorted([(pt, f) for (f, t, pf, pt) in E if t == n]))
           for n, (tp, ar) in V.items()
           if tp == 'flip-flop'
    ]
    internal_wires = [
        ((n, tp, ar),
         sorted([(pt, f) for (f, t, pf, pt) in E if t == n]))
        for (n, (tp, ar)) in V.items()
        if tp not in ('input', 'output', 'flip-flop')
    ]
    output_wires = [
        ((n, tp, ar),
         sorted([(pt, f) for (f, t, pf, pt) in E if t == n]))
        for (n, (tp, ar)) in V.items()
        if tp == 'output'
    ]

    kwargs = {
        'inouts' : inouts,
        'ins' : ins,
        'outs' : outs,
        'internal_wires' :  internal_wires,
        'output_wires' : output_wires,
        'ffs' : ffs,
        'mod_name' : mod_name,

        # Rendering functions
        'render_lval' : render_lval,
        'render_rval' : render_rval,
    }
    render_tmpl_to_file('module.v', f'{mod_name}.v', **kwargs)

def render_verilog_tb(V, E, mod_name, clk_n_rstn):
    def fmt_arity(ar):
        return '%5b' if ar == 1 else '%5d'

    ins = input_nodes(V)
    outs = output_nodes(V)
    inouts = ins + outs

    value_fmts = [fmt_arity(ar) for (n, ar) in inouts]
    header_fmts = ['%5s' for _ in inouts]
    names = [n for (n, ar) in inouts]
    quoted_names = [f'"{n}"' for n in names]


    ranges = [list(range(2**ar)) for (_, ar) in ins]

    assignments = list(product(*ranges))



    kw = {
        'mod_name' : mod_name,

        'ins' : ins,
        'outs' : outs,

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
    render_tmpl_to_file('tb.v', f'{mod_name}_tb.v', **kw)

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

def plot_hw_graph(V, E, mod_name, draw_clk):
    G = AGraph(strict = False, directed = True)
    graph_attrs = {
        'dpi' : 300,
        'ranksep' : 0.4,
        'fontname' : 'Inconsolata',
        'bgcolor' : 'transparent',
        #'splines' : 'ortho',
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


    file_path = f'{mod_name}.png'
    G.draw(file_path, prog='dot')

def main():
    # V = {'x' : ('input', 1),
    #      'y' : ('input', 1),
    #      'z' : ('output', 1),
    #      'xy' : ('or', 1)
    # }
    # E = {
    #     ('x', 'xy', 0, 0),
    #     ('y', 'xy', 0, 1),
    #     ('xy', 'z', 0, 0)
    # }
    # V = {
    #     'clk' : ('input', 1),
    #     'rstn' : ('input', 1),
    #     'o' : ('output', 3),
    #     'ff' : ('flip-flop', 3),
    #     'c1' : ('const_1', 3),
    #     'c0' : ('const_0', 3),
    #     'cnt' : ('add', 3),
    #     'sel' : ('not', 1),
    #     'ff_next' : ('mux2', 3)
    # }
    # E = {
    #     ('rstn', 'sel', 0, 0),
    #     ('sel', 'ff_next', 0, 0),
    #     ('c0', 'ff_next', 0, 1),
    #     ('cnt', 'ff_next', 0, 2),
    #     ('clk', 'ff', 0, 0),
    #     ('ff_next', 'ff', 0, 1),
    #     ('ff', 'o', 0, 0),
    #     ('ff', 'cnt', 0, 0),
    #     ('c1', 'cnt', 0, 1)
    # }
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

        'begin_p' : ('and', 1),
        'continue_p' : ('or', 1),

        'not_p' : ('not', 1),
        'not_rstn' : ('not', 1),

        'x_ge_y' : ('ge', 1),
        'y_eq_0' : ('eq', 1),
        'y_sub_x' : ('sub', 8),

        'y_eq_0_and_p' : ('and', 1),


        'p_next' : ('mux2', 1),
        'x_next' : ('mux2', 8),
        'y_next' : ('mux2', 8),

        'x_next2' : ('mux2', 8),
        'y_next2' : ('mux2', 8),

        'x_next3' : ('mux2', 8),
        'y_next3' : ('mux2', 8),

        'p' : ('flip-flop', 1),
        'x' : ('flip-flop', 8),
        'y' : ('flip-flop', 8)
    }
    E = {
        # Clock connections
        ('clk', 'p', 0, 0),
        ('clk', 'x', 0, 0),
        ('clk', 'y', 0, 0),

        # Connect registers
        ('p_next', 'p', 0, 1),
        ('x_next', 'x', 0, 1),
        ('y_next', 'y', 0, 1),

        # not_p
        ('p', 'not_p', 0, 0),

        # not_p
        ('rstn', 'not_rstn', 0, 0),

        # begin_p
        ('in_valid', 'begin_p', 0, 0),
        ('not_p', 'begin_p', 0, 0),

        # continue_p
        ('p', 'continue_p', 0, 0),
        ('in_valid', 'continue_p', 0, 0),

        # x_ge_y
        ('x', 'x_ge_y', 0, 0),
        ('y', 'x_ge_y', 0, 1),

        # y_eq_0
        ('y', 'y_eq_0', 0, 0),
        ('c0_8', 'y_eq_0', 0, 1),

        # y_sub_x
        ('y', 'y_sub_x', 0, 0),
        ('x', 'y_sub_x', 0, 1),

        # x_next2
        ('p', 'x_next2', 0, 0),
        ('x_next3', 'x_next2', 0, 1),
        ('x', 'x_next2', 0, 2),

        # x_next3
        ('x_ge_y', 'x_next3', 0, 0),
        ('y', 'x_next3', 0, 1),
        ('x', 'x_next3', 0, 2),

        # y_next2
        ('p', 'y_next2', 0, 0),
        ('y_next3', 'y_next2', 0, 1),
        ('y', 'y_next2', 0, 2),

        # y_next3
        ('x_ge_y', 'y_next3', 0, 0),
        ('x', 'y_next3', 0, 1),
        ('y_sub_x', 'y_next3', 0, 2),


        # Connect next muxes
        ('not_rstn', 'p_next', 0, 0),
        ('c0_1', 'p_next', 0, 1),
        ('continue_p', 'p_next', 0, 2),

        ('begin_p', 'x_next', 0, 0),
        ('a', 'x_next', 0, 1),
        ('x_next2', 'x_next', 0, 2),

        ('begin_p', 'y_next', 0, 0),
        ('b', 'y_next', 0, 1),
        ('y_next2', 'y_next', 0, 2),

        # Stuff for p
        ('not_p', 'in_ready', 0, 0),


        # Other stuff
        ('y_eq_0', 'y_eq_0_and_p', 0, 0),
        ('p', 'y_eq_0_and_p', 0, 1),
        ('y_eq_0_and_p', 'out_valid', 0, 0),
        ('x', 'o', 0, 0)
    }
    # render_verilog(V, E, 'test01')
    # render_verilog_tb(V, E, 'test01', ('clk', 'rstn'))
    plot_hw_graph(V, E, 'test01', False)



main()
