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
    'output' : '#7788aa',
    'input' : '#cc8877',

    # Slices and registers have the same color since they usually
    # refer to the same data.
    'reg' : '#bb77bb',
    'slice' : '#bb77bb',
    None : '#6ca471'
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
IF_EDGE_ARROWHEAD_COLORS = {0 : 'black', 1 : '#00aa00', 2 : '#aa0000'}

def colorize(s, col):
    return '<font color="%s">%s</font>' % (col, s)

def draw_label(v, draw_arities, draw_names):
    n = v.name
    tp = v.type.name
    tp_col = TYPE_TO_NAME_COLOR.get(tp, TYPE_TO_NAME_COLOR[None])
    if tp in {'cast', 'cat', 'slice', 'reg', 'if'}:
        label = tp
    elif tp == 'const':
        label = f'{v.value}'
    elif tp in {'input', 'output'}:
        label = colorize(n, tp_col)
    elif tp in UNARY_OPS | BINARY_OPS:
        label = escape(TYPE_TO_SYMBOL.get(tp, ''))
    else:
        assert False
    if v.refer_by_name and draw_names:
        var = colorize(n, tp_col)
        label = f'{var} &larr; {label}'
    if draw_arities:
        label = f'{label}:{v.arity or "?"}'
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

def style_edge(pt, v1, v2):
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
    return {
        'color' : color,
        'style' : style,
        'penwidth' : penwidth
        }

def setup_graph():
    G = AGraph(strict = False, directed = True)
    graph_attrs = {
        'dpi' : 150,
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

def plot_vertices(vertices, png_path,
                  draw_clk, draw_arities, draw_names):
    G = setup_graph()

    for v in vertices:
        if v.name != 'clk' or draw_clk:
            G.add_node(v.name,
                       label = draw_label(v, draw_arities, draw_names),
                       **style_node(v))

    for v2 in vertices:
        for i, v1 in enumerate(v2.predecessors):
            if v1 and v1.name != 'clk' or draw_clk:
                attrs = style_edge(i, v1, v2)
                G.add_edge(v1.name, v2.name, **attrs)
    G.draw(png_path, prog='dot')

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
        return '%s[%s:%s]' % r_args
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

def expression_label(v, edges):
    label = expression_label_rec(v, None, v, edges)
    tp = v.type.name
    if tp != 'reg' and (v.refer_by_name or tp == 'output'):
        col = TYPE_TO_NAME_COLOR.get(tp, TYPE_TO_NAME_COLOR[None])
        var = colorize(v.name, col)
        label = f'{var} &larr; {label}'
    return f'<{label}>'

def is_expression(v):
    # Expressions are the following:
    #   1) registers, ifs, and outputs
    #   2) aliased vertices, unless they are slices
    #   3) vertices whose successors can't "consume" them
    tp = v.type.name
    if tp == 'slice':
        return False
    elif tp in {'reg', 'if', 'output'}:
        return True
    elif v.refer_by_name:
        return True
    for s in v.successors:
        child_idx = s.predecessors.index(v)
        if s.type.name in {'if', 'reg'} and child_idx != 0:
            return True
    return False


def plot_expressions(vertices, png_path):
    G = setup_graph()
    exprs = [v for v in vertices if is_expression(v)]
    edges = set()
    for v in exprs:
        label = expression_label(v, edges)
        G.add_node(v.name,
                   label = label,
                   **style_node(v))
    for v1, v2, i in edges:
        kw = style_edge(i, v1, v2)
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
