# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from html import escape
from hwgraph import (UNARY_OPS, BINARY_OPS, TYPE_TO_SYMBOL, Vertex,
                     package_vertex)
from pygraphviz import AGraph

# Todo: Define child and parent better.
# predecessors => parents
# successors => children
# A little weird since children contain their parents.

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
    'reg' : '#ffffdd',
    None : 'white'
}
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
        value = v.output['o'].value
        label = str(value)
    elif tp in {'input', 'output'}:
        label = colorize(n, tp_col)
    elif tp in UNARY_OPS | BINARY_OPS:
        label = escape(TYPE_TO_SYMBOL.get(tp, ''))
    else:
        assert False
    if v.refer_by_name and draw_names:
        var = colorize(n, tp_col)
        label = f'{var} &larr; {label}'
    return f'<{label}>'

def style_node(v):
    n, tp = v.name, v.type.name

    shape = TYPE_TO_SHAPE.get(tp, TYPE_TO_SHAPE[None])
    fillcolor = TYPE_TO_FILLCOLOR.get(tp, TYPE_TO_FILLCOLOR[None])
    width = height = TYPE_TO_SIZE.get(tp, TYPE_TO_SIZE[None])

    return {'shape' : shape,
            'width' : width,
            'height' : height,
            'color' : 'black',
            'fillcolor' : fillcolor}

def style_edge(pt, v1, v2, draw_arities):
    color = 'black'
    style = 'solid'
    penwidth = 0.5
    tp2 = v2.type.name
    if tp2 == 'if':
        color = f'black;0.9999:%s' % IF_EDGE_ARROWHEAD_COLORS[pt]
    elif tp2 == 'reg':
        if pt == 0:
            style = 'dashed'
    if v1.arity != 1:
        penwidth = 1.0
    style = {
        'color' : color,
        'style' : style,
        'penwidth' : penwidth
    }
    if draw_arities:
        style['label'] = ' %d' % v1.arity
    return style

def style_edge2(v1, pin_out, v2, pin_in, draw_arities, draw_pins):
    style = 'solid'
    penwidth = 0.5
    wire  = v1.output[pin_out]
    if wire.arity != 1:
        penwidth = 1.0

    tp2 = v2.type
    pin_in_idx = tp2.input.index(pin_in)
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
        if len(v2.input) > 1:
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
        'rankdir' : 'TB'
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

def plot_vertices(vertices, png_path,
                  group_by_type, draw_clk, draw_names,
                  draw_arities, draw_pins):
    G = setup_graph()
    tp_graphs = {}
    for v in vertices:
        print(v.name, v.name == 'clk' and not draw_clk)
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
    for v2 in vertices:
        for i, (v1, pin_out) in enumerate(v2.input):
            if v1.name == 'clk' and not draw_clk:
                continue
            pin_in = v2.type.input[i]
            attrs = style_edge2(v1, pin_out, v2, pin_in,
                                draw_arities,
                                draw_pins)
            G.add_edge(v1.name, v2.name, **attrs)

    G.draw(png_path, prog='dot')
    print(G)

def expression_label_reg(v):
    col = TYPE_TO_NAME_COLOR['reg']
    fmt = '%s &larr; [%d:%d]'

    top = None
    if v.refer_by_name:
        top = fmt % (colorize(v.name, col), v.arity - 1, 0)

    slices = [(v2.predecessors[1].value, v2.predecessors[2].value, v2.name)
              for v2 in v.successors if (v2.type.name == 'slice' and
                                         v2.refer_by_name)]
    slices = reversed(sorted(slices))
    slices = [fmt % (colorize(n, col), hi, lo) for hi, lo, n in slices]
    slices = '|'.join(slices)
    if top:
        return '{ %s |{%s}}' % (top, slices) if slices else top
    return slices

def expression_input(parent, child, v_expr, edges):
    parent_tp = parent.type.name
    child_tp = child.type.name
    parent_idx = child.predecessors.index(parent)
    if child_tp in {'reg', 'if'} and parent_idx != 0:
        edges.add((parent, v_expr, parent_idx))
        return None
    elif parent.refer_by_name or parent_tp == 'output':
        col = TYPE_TO_NAME_COLOR.get(parent_tp, TYPE_TO_NAME_COLOR[None])
        return colorize(parent.name, col)
    elif parent_tp in {'if', 'reg'}:
        edges.add((parent, v_expr, parent_idx))
        return '*'
    return expression_label_rec(parent, child, v_expr, edges)

def expression_label_rec(parent, child, v_expr, edges):
    tp = parent.type.name
    sym = escape(TYPE_TO_SYMBOL.get(tp, ''))
    r_args = tuple([expression_input(p, parent, v_expr, edges)
                    for p in parent.predecessors])
    if tp == 'slice':
        return '[%s:%s]' % r_args[1:]
    elif tp == 'reg':
        return expression_label_reg(parent)
    elif tp == 'cast':
        return "%s'(%s)" % r_args
    elif tp == 'const':
        val = parent.value
        return str(val)
    elif tp == 'output':
        return r_args[0]
    elif tp == 'input':
        return colorize(parent.name, TYPE_TO_NAME_COLOR[tp])
    elif tp in UNARY_OPS:
        return '%s%s' % (sym, r_args[0])
    elif tp in BINARY_OPS:
        s = '%s %s %s' % (r_args[0], sym, r_args[1])
        return package_vertex(parent, child) % s
    elif tp == 'cat':
        s = '%s, %s' % (r_args[0], r_args[1])
        return package_vertex(parent, child) % s
    elif tp == 'if':
        return r_args[0]
    assert False

def expression_input2(v_at, v_succ, edges):
    return expression_label_rec2(v_at, v_succ, edges)

def expression_label_rec2(v_at, v_succ, edges):
    tp = v_at.type.name
    sym = escape(TYPE_TO_SYMBOL.get(tp, ''))

    args = tuple([expression_input2(v, v_at, edges)
                  for (v, _) in v_at.input])

    if tp == 'output':
        return args[0]
    elif tp == 'input':
        return colorize(v_at.name, TYPE_TO_NAME_COLOR[tp])
    elif tp in BINARY_OPS:
        s = '%s %s %s' % (args[0], sym, args[1])
        return package_vertex(v_succ, v_at) % s
    else:
        assert False

def expression_label(v, edges):
    label = expression_label_rec2(v, None, edges)
    tp = v.type.name
    if tp != 'reg' and (v.refer_by_name or tp == 'output'):
        col = TYPE_TO_NAME_COLOR.get(tp, TYPE_TO_NAME_COLOR[None])
        var = colorize(v.name, col)
        label = f'{var} &larr; {label}'
    return f'<{label}>'

def owns_expression(v):

    # A vertex owns an experssion if
    #
    #   1) it is a register, if, or output node;
    #   2) it has an alias and is not a slice; or
    #   3) it has an output pin connected to a vertex that cannot
    #   "consume" it.
    tp = v.type.name
    if tp == 'slice':
        return False
    elif tp in {'reg', 'if', 'output'}:
        return True
    elif v.refer_by_name:
        return True

    # Fix this logic.
    for pin, wire in v.output.items():
        pass
    # for s in v.successors:
    #     child_idx = s.predecessors.index(v)
    #     if s.type.name in {'if', 'reg'} and child_idx != 0:
    #         return True
    return False


def plot_expressions(vertices, png_path, draw_arities):
    G = setup_graph()
    exprs = [v for v in vertices if owns_expression(v)]

    edges = set()
    for v in exprs:
        label = expression_label(v, edges)
        G.add_node(v.name,
                   label = label,
                   **style_node(v))

    for v1, v2, i in edges:
        kw = style_edge(i, v1, v2, draw_arities)
        G.add_edge(v1.name, v2.name, **kw)

    # Create invisible between vertices lacking edges.
    trivial_exprs = set(exprs)
    for v1, v2, i in edges:
        trivial_exprs -= {v1, v2}

    trivial_exprs = sorted(trivial_exprs,
                           key = lambda v: v.type.name == 'output')
    for v1, v2 in zip(trivial_exprs, trivial_exprs[1:]):
        G.add_edge(v1.name, v2.name, style='invis')
    G.draw(png_path, prog='dot')
