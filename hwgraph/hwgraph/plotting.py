# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from html import escape
from hwgraph import UNARY_OPS, BINARY_OPS, TYPE_TO_SYMBOL, Vertex
from pygraphviz import AGraph

# Internalization... For now only used to improve plotting.
INTERNALIZABLE_TYPES = {'cat', 'const', 'input'} | BINARY_OPS | UNARY_OPS

def clone_vertex(v1):
    v2 = Vertex(v1.name, v1.type, v1.arity, v1.value)
    v2.internalized = v1.internalized
    return v2

def replace_vertex_pred(v, old, new):
    idx = v.predecessors.index(old)
    v.predecessors[idx] = new
    new.successors.append(v)

def clone_simple_vertices(vertices):
    # Duplicate some trivial nodes.
    clones = []
    for v1 in vertices:
        tp = v1.type.name
        if any(v1.predecessors):
            continue
        # What about comparisons?
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
            tp = v.type.name
            if tp in {'cat', 'slice', 'if'} | BINARY_OPS | UNARY_OPS:
                for i, p in enumerate(list(v.predecessors)):
                    if (p and
                        p.type.name in INTERNALIZABLE_TYPES and
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

def colorize(s, col):
    return '<font color="%s">%s</font>' % (col, s)

def render_label(v, parent_tp):
    tp = v.type.name
    sym = escape(TYPE_TO_SYMBOL.get(tp, ''))
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
        if interns:
            x = render_label(interns[0], tp)
            return f'{sym}{x}'
        return sym
    elif tp in BINARY_OPS:
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

def style_node(v, draw_arities, draw_aliases):
    n, tp = v.name, v.type.name

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

    if v.alias and draw_aliases:
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
    tp2 = v2.type.name
    if tp2 == 'if':
        if pt == 1:
            color = 'black;0.9999:#00aa00'
        elif pt == 2:
            color = 'black;0.9999:#aa0000'
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
                  draw_clk, draw_arities, draw_aliases):
    G = setup_graph()

    # Vertices names are not always unique.
    ids = {v : i for i, v in enumerate(vertices)}

    for v in vertices:
        if v.name != 'clk' or draw_clk:
            attrs = style_node(v, draw_arities, draw_aliases)
            G.add_node(ids[v], **attrs)

    for v2 in vertices:
        for i, v1 in enumerate(v2.predecessors):
            if v1 and v1.name != 'clk' or draw_clk:
                attrs = style_edge(i, v1, v2)
                G.add_edge(ids[v1], ids[v2], **attrs)
    G.draw(png_path, prog='dot')
