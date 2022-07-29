# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from html import escape
from hwgraph import UNARY_OPS, BINARY_OPS, Vertex, package_expr
from hwgraph.types import TYPE_SYMBOLS, TYPES
from pygraphviz import AGraph

TYPE_TO_NAME_COLOR = {
    'output' : '#bb77bb',
    'input' : '#cc8877',

    # Slices and registers have the same color since they usually
    # refer to the same data.
    'reg' : '#7788aa',
    'slice' : '#7788aa',
    None : '#6ca471'
}
IF_EDGE_ARROWHEAD_COLORS = {
    0 : 'black',
    1 : '#00aa00',
    2 : '#aa0000'
}

TYPE_TO_SHAPE = {
    'input' : 'oval',
    'output' : 'oval',
    'if' : 'diamond',
    'reg' : 'record',
    None : 'box'
}
TYPE_TO_FILLCOLOR = {
    TYPES['reg'] : '#ffffdd',
}
MODULE_FILLCOLOR = '#e0f0ff'
DEFAULT_FILLCOLOR = 'white'

TYPE_TO_SIZE = {
    'const' : 0.3,
    None : 0.55
}

def colorize(s, col):
    return '<font color="%s">%s</font>' % (col, s)

def draw_label(v, draw_names):
    n = v.name
    tp = v.type.name
    tp_col = TYPE_TO_NAME_COLOR.get(tp, TYPE_TO_NAME_COLOR[None])
    if tp in {'cast', 'cat', 'if', 'reg', 'slice'}:
        label = tp
    elif tp in {'full_adder'}:
        return n
    elif tp == 'const':
        value = v.output[0].value
        label = str(value)
    elif tp in {'input', 'output'}:
        label = colorize(n, tp_col)
    elif tp in UNARY_OPS | BINARY_OPS:
        label = escape(TYPE_SYMBOLS.get(tp, ''))
    else:
        assert False
    if v.refer_by_name and draw_names:
        var = colorize(n, tp_col)
        label = f'{var} &larr; {label}'
    return f'<{label}>'

def style_node(v):
    n, tp = v.name, v.type.name

    shape = TYPE_TO_SHAPE.get(tp, TYPE_TO_SHAPE[None])

    if v.type in TYPE_TO_FILLCOLOR:
        fillcolor = TYPE_TO_FILLCOLOR[v.type]
    elif v.type.is_module:
        fillcolor = MODULE_FILLCOLOR
    else:
        fillcolor = DEFAULT_FILLCOLOR
    width = height = TYPE_TO_SIZE.get(tp, TYPE_TO_SIZE[None])
    return {'shape' : shape,
            'width' : width,
            'height' : height,
            'color' : 'black',
            'fillcolor' : fillcolor}

def style_edge(dst, wire, pin_in_idx, draw_arities, draw_pins):
    style = 'solid'
    penwidth = 0.5

    if wire.arity != 1:
        penwidth = 1.0

    tp2 = dst.type
    tp2name = tp2.name
    color = 'black'
    if tp2name == 'if':
        color = f'black;0.9999:%s' % IF_EDGE_ARROWHEAD_COLORS[pin_in_idx]
    elif tp2name == 'reg' and pin_in_idx == 0:
        style = 'dashed'

    attrs = {
        'color' : color,
        'style' : style,
        'penwidth' : penwidth
    }
    if draw_arities:
        attrs['label'] = ' %s' % wire.arity
    if draw_pins:
        if len(dst.input) > 1:
            attrs['headlabel'] = pin_in
        if len(v1.output) > 1:
            attrs['taillabel'] = pin_out
    return attrs

def setup_graph():
    G = AGraph(strict = False, directed = True)
    graph_attrs = {
        'dpi' : 150,
        'ranksep' : 0.3,
        'fontname' : 'Inconsolata',
        'bgcolor' : 'transparent',
        'rankdir' : 'TB',
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
        'fontsize' : '10pt',
        'arrowsize' : 0.7
    }
    G.edge_attr.update(edge_attrs)
    return G

def get_input_wire(dst, idx):
    src, pin = dst.input[idx]
    return src.output[pin]

def expression_label_reg(v):
    col = TYPE_TO_NAME_COLOR['reg']
    fmt = '%s &larr; [%d:%d]'

    arity = v.output[0].arity

    top = None
    if v.refer_by_name:
        top = fmt % (colorize(v.name, col), arity - 1, 0)

    slices = [(get_input_wire(v2, 1).value,
               get_input_wire(v2, 2).value,
               v2.name)
              for v2 in v.output[0].destinations
              if (v2.type.name == 'slice' and v2.refer_by_name)]

    slices = reversed(sorted(slices))
    slices = [fmt % (colorize(n, col), hi, lo) for hi, lo, n in slices]
    slices = '|'.join(slices)
    if top:
        return '{ %s |{%s}}' % (top, slices) if slices else top
    return slices

def port_out_name(v, out_pin):
    n = v.name
    output = v.type.output
    if len(output) == 1:
        assert out_pin == 0
        return n
    return '%s.%s' % (n, output[out_pin])

def expression_input(src, dst, root, pin_in_idx, edges):
    dst_tp = dst.type.name
    src_tp = src.type.name
    col = TYPE_TO_NAME_COLOR.get(src_tp, TYPE_TO_NAME_COLOR[None])
    if dst_tp in {'reg', 'if'} and pin_in_idx != 0:
        assert len(src.output) == 1
        edges.add((src, root, src.output[0], pin_in_idx))
        return None
    elif src_tp == 'output':
        return colorize(src.name, col)
    elif src.refer_by_name:
        _, pin_out_idx = dst.input[pin_in_idx]
        s = port_out_name(src, pin_out_idx)
        return colorize(s, col)
    elif src_tp in {'if', 'reg'} or src.type.is_module:
        _, pin_out_idx = dst.input[pin_in_idx]
        edges.add((src, root, src.output[pin_out_idx], pin_in_idx))
        return '*'
        edges.add((src, root, src.output[0], pin_in_idx))
        return '*'

    return expression_label_rec(src, dst, root, edges)

def expression_label_rec(src, dst, root, edges):
    tp = src.type.name
    name = src.name
    sym = escape(TYPE_SYMBOLS.get(tp, ''))

    args = tuple([expression_input(v, src, root, pin_in_idx, edges)
                  for pin_in_idx, (v, _) in enumerate(src.input)])

    if tp == 'output':
        return args[0]
    elif tp == 'slice':
        return '%s[%s:%s]' % args
    elif tp == 'cast':
        return "%s'(%s)" % args
    elif tp == 'if':
        return args[0]
    elif tp == 'full_adder':
        return 'FA{%s}' % ', '.join(args)
    elif tp == 'reg':
        return expression_label_reg(src)
    elif tp == 'input':
        return colorize(name, TYPE_TO_NAME_COLOR[tp])
    elif tp == 'const':
        return str(src.output[0].value)
    elif tp in UNARY_OPS:
        return '%s%s' % (sym, args[0])
    elif tp in BINARY_OPS:
        s = '%s %s %s' % (args[0], sym, args[1])
        return package_expr(src, dst) % s
    elif tp == 'cat':
        s = '%s, %s' % args
        return package_expr(src, dst) % s
    else:
        print(tp)
        assert False

def expression_label(v, edges):
    label = expression_label_rec(v, None, v, edges)
    tp = v.type.name
    if tp != 'reg' and (v.refer_by_name or tp == 'output'):
        col = TYPE_TO_NAME_COLOR.get(tp, TYPE_TO_NAME_COLOR[None])
        var = colorize(v.name, col)
        label = f'{var} &larr; {label}'
    return f'<{label}>'

def owns_expression(v1):
    # A vertex owns an experssion if
    #
    #   1) it is a register, if, or output node;
    #   2) it has an alias and is not a slice; or
    #   3) it has an output pin connected to a vertex that cannot
    #   "consume" it.
    tp = v1.type.name
    if tp == 'slice':
        return False
    elif tp in {'reg', 'if', 'output'}:
        return True
    elif v1.refer_by_name:
        return True
    elif v1.type.is_module:
        return True

    for pin_out, wire in enumerate(v1.output):
        out_port = v1, pin_out
        for v2 in wire.destinations:
            pin_in_idx = v2.input.index(out_port)
            # Not quite.
            if v2.type.name in {'if', 'reg'} and pin_in_idx != 0:
                return True
    return False

# Sometimes topological sort improves the layout. Sometimes it does
# not.
def bfs_order(vertices):
    worklist = [v for v in vertices if len(v.input) == 0]
    seen = set()
    while worklist:
        v = worklist.pop(0)
        yield v
        if v in seen:
            continue
        for wire in v.output:
            worklist.extend(wire.destinations)
        seen.add(v)

def plot_vertices(vertices, png_path,
                  group_by_type, draw_clk, draw_names,
                  draw_arities, draw_pins):

    G = setup_graph()
    tp_graphs = {}

    # For gcd.json, sorting by type improves the layout a lot.
    vertices = sorted(vertices,
                      key = lambda v: v.type.name)

    for v in vertices:
        if v.name == 'clk' and not draw_clk:
            continue
        g = G
        if group_by_type:
            tp = v.type.name
            if tp not in tp_graphs:
                tp_graphs[tp] = G.add_subgraph(name = tp, rank = 'same')
            g = tp_graphs[tp]
        g.add_node(v.name,
                   label = draw_label(v, draw_names),
                   **style_node(v))

    for dst in vertices:
        for pin_in_idx, (src, pin_out) in enumerate(dst.input):
            if src.name == 'clk' and not draw_clk:
                continue
            wire = src.output[pin_out]
            kw = style_edge(dst, wire, pin_in_idx,
                            draw_arities, draw_pins)
            G.add_edge(src.name, dst.name, **kw)
    G.draw(png_path, prog='dot')

def plot_expressions(vertices, png_path,
                     group_by_type,
                     draw_arities):

    # Sorting helps Graphviz
    vertices = sorted(vertices, key = lambda v: v.type.name)

    vertices = [v for v in vertices if owns_expression(v)]
    G = setup_graph()
    tp_graphs = {}
    edges = set()
    for v in vertices:
        label = expression_label(v, edges)
        g = G
        if group_by_type:
            tp = v.type.name
            if tp not in tp_graphs:
                tp_graphs[tp] = G.add_subgraph(name = tp, rank = 'same')
            g = tp_graphs[tp]
        g.add_node(v.name, label = label, **style_node(v))

    for src, dst, wire, pin_in_idx in edges:
        kw = style_edge(dst, wire, pin_in_idx, draw_arities, False)
        G.add_edge(src.name, dst.name, **kw)

    # Create invisible eges between vertices lacking edges.
    trivial_exprs = set(vertices)
    for v1, v2, _, _ in edges:
        trivial_exprs -= {v1, v2}

    trivial_exprs = sorted(trivial_exprs,
                           key = lambda v: v.type.name == 'output')
    for v1, v2 in zip(trivial_exprs, trivial_exprs[1:]):
        G.add_edge(v1.name, v2.name, style='invis')
    G.draw(png_path, prog='dot')
