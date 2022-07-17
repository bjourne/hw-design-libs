# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from html import escape
from hwgraph import (UNARY_OPS, BINARY_OPS, TYPE_TO_SYMBOL, Vertex,
                     requires_brackets)
from pygraphviz import AGraph

TYPE_TO_NAME_COLOR = {
    'output' : '#7788aa',
    'input' : '#aa8888',
    None : '#6ca471'
}
TYPE_TO_SHAPE = {
    'input' : 'oval',
    'output' : 'oval',
    'if' : 'diamond',
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
    if tp in {'slice', 'reg', 'if', 'cat'}:
        label = tp
    elif tp == 'const':
        label = f'{v.value}'
    elif tp in {'input', 'output'}:
        label = colorize(n, TYPE_TO_NAME_COLOR[tp])
    elif tp in UNARY_OPS | BINARY_OPS:
        label = escape(TYPE_TO_SYMBOL.get(tp, ''))
    else:
        assert False
    if v.refer_by_name and draw_names:
        var = colorize(n, TYPE_TO_NAME_COLOR[None])
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

def statement_label(v, parent, root, edges):
    def render_pred(v, parent, edges):
        tp = v.type.name
        parent_idx = parent.predecessors.index(v)
        if v.refer_by_name or tp == 'output':
            col = TYPE_TO_NAME_COLOR.get(tp, TYPE_TO_NAME_COLOR[None])
            return colorize(v.name, col)
        elif tp in {'if', 'reg'}:
            edges.add((v, root, parent_idx))
            return '*'
        return statement_label(v, parent, root, edges)

    name = v.name
    tp = v.type.name
    ps = v.predecessors
    sym = escape(TYPE_TO_SYMBOL.get(tp, ''))
    parent_tp = parent.type.name if parent else None
    rendered_ps = tuple([render_pred(p, v, edges) for p in ps])

    if tp == 'slice':
        return '%s[%s:%s]' % rendered_ps
    elif tp == 'reg':
        return rendered_ps[1]
    elif tp == 'const':
        return f'{v.value}'
    elif tp == 'output':
        return rendered_ps[0]
    elif tp == 'input':
        return colorize(name, TYPE_TO_NAME_COLOR[tp])
    elif tp in UNARY_OPS:
        return '%s%s' % (sym, rendered_ps[0])
    elif tp in BINARY_OPS:
        s = '%s %s %s' % (rendered_ps[0], sym, rendered_ps[1])
        if requires_brackets(v, parent):
            s = f'({s})'
        return s
    elif tp == 'cat':
        s = '%s, %s' % (rendered_ps[0], rendered_ps[1])
        if requires_brackets(v, parent):
            s = '{%s}' % s
        return s
    elif tp == 'if':
        return '%s<br/>? %s<br/>: %s' % rendered_ps
    assert False

def draw_statement_label(v, edges):
    label = statement_label(v, None, v, edges)
    if v.refer_by_name or v.type.name == 'output':
        col = TYPE_TO_NAME_COLOR.get(v.type.name, TYPE_TO_NAME_COLOR[None])
        var = colorize(v.name, col)
        label = f'{var} &larr; {label}'
    return f'<{label}>'

def plot_statements(vertices, png_path):
    G = setup_graph()

    vertices = [v for v in vertices
                if (v.type.name in {'reg', 'if', 'output'} or
                    v.refer_by_name)]

    edges = set()
    for v in vertices:
        label = draw_statement_label(v, edges)
        G.add_node(v.name,
                   label = label,
                   **style_node(v))
    for v1, v2, i in edges:
        kw = style_edge(i, v1, v2)
        G.add_edge(v1.name, v2.name, **kw)

    G.draw(png_path, prog='dot')
