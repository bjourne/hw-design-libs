# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from hwgraph import (BINARY_OPS,
                     UNARY_OPS, TYPE_TO_SYMBOL,
                     Vertex,
                     package_vertex)
from itertools import groupby
from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template
from more_itertools import partition
from pathlib import Path

TMPL_PATH = Path(__file__).parent / 'templates'
ENV = Environment(loader = FileSystemLoader(TMPL_PATH),
                  undefined = StrictUndefined)
INDENT = ' ' * 4

def render_tmpl_to_file(tmpl_name, file_path, **kwargs):
    tmpl = ENV.get_template(tmpl_name)
    txt = tmpl.render(**kwargs)
    with open(file_path, 'wt') as of:
        of.write(txt + '\n')

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

def groupby_sort(seq, keyfun):
    grps = groupby(seq, keyfun)
    grps = [(k, list(v)) for k, v in grps]
    return sorted(grps)

def output_name(v1, pin_idx):
    wire = v1.output[pin_idx]
    dests = wire.destinations
    if len(dests) == 1:
        v2 = dests[0]
        if v2.type.name == 'output':
            return v2.name, False, None
    name = '%s_%s' % (v1.name, v1.type.output[pin_idx])
    return name, True, wire.arity

def input_wire_name(v1, pin):
    if v1.type.name == 'input':
        return v1.name
    return '%s_%s' % (v1.name, pin)

def render_submod_args(v):
    output = [output_name(v, i) for i in range(len(v.output))]
    new_wires = [(n, a) for (n, new, a) in output if new]
    output = [n for n, _, _ in output]
    input = [input_wire_name(v2, pin)
             for v2, pin in v.input]
    return input + output, new_wires

def type_name(v):
    return v.type.name

def vertex_arity(v):
    tp = v.type.name
    if tp in {'input', 'const'}:
        return v.output[0].arity
    elif tp == 'output':
        v, pin = v.input[0]
        return v.output[0].arity
    assert False

def group_inputs_and_outputs(by_type, input_tp, output_tp):
    input = by_type['input']
    output = by_type['output']
    gr_ins = groupby_sort(input, vertex_arity)
    gr_outs = groupby_sort(output, vertex_arity)
    io_groups = [(input_tp, gr_ins), (output_tp, gr_outs)]
    return io_groups, input, output

def format_inouts(n, input, output):
    input = ', '.join(v.name for v in input)
    output = ', '.join(v.name for v in output)
    if input and output:
        return input + ',\n' + n * INDENT + output
    return input + output

def render_module(vertices, mod_name, path):

    def is_type(v, tp):
        return type_name(v) == tp

    vs_by_type = dict(groupby_sort(vertices, type_name))
    io_groups, input, output = \
        group_inputs_and_outputs(vs_by_type, 'input', 'output')

    # Group registers by driving clock.
    regs = vs_by_type.get('reg', [])
    regs_per_clk = groupby_sort(regs, lambda v: v.input[0][0].name)

    others, regs = partition(lambda v: is_type(v, 'reg'), vertices)
    others, explicit = partition(lambda v: v.refer_by_name, others)
    others, implicit = partition(lambda v: is_type(v, 'if'), others)
    others, submods = partition(lambda v: is_type(v, 'full_adder'), others)

    submods = list(submods)

    submod_names = sorted({v.type.name for v in submods
                           if v.type.is_module})
    submods = [(v, render_submod_args(v)) for v in submods]

    kwargs = {
        'mod_name' : mod_name,
        'submod_names' : submod_names,
        'inouts' : format_inouts(1, input, output),
        'io_groups' : io_groups,
        'submods' : submods
    }
    render_tmpl_to_file('module2.v', path / f'{mod_name}.v', **kwargs)

def flatten(seq):
    return [y for x in seq for y in x]

def ansi_escape(s, tp, col):
    return '%%c[%d;%dm' % (tp, col) + s + '%c[0m'

def fmt_arity(v, ind):
    size = max(5, len(v.name))
    if not ind:
        ind = 'b' if vertex_arity(v) == 1 else 'd'
    return f'%{size}{ind}'

def render_args(vs, quote):
    args = [['27', f'"{v.name}"' if quote else v.name, '27']
            for v in vs]
    args = flatten(args)
    return ', '.join(args)

def render_fmts(vs, ind):
    colors = {
        'input' : 36,
        'output' : 33,
        'const' : 37
    }
    fmt_cols = [(fmt_arity(v, ind), colors[v.type.name]) for v in vs]
    fmts = [ansi_escape(fmt, 1, col) for fmt, col in fmt_cols]
    return ' '.join(fmts)

def render_tb(types, vertices, tests, mod_name, path):
    vs_by_type = dict(groupby_sort(vertices, type_name))
    io_groups, input, output = \
        group_inputs_and_outputs(vs_by_type, 'reg', 'wire')
    inouts_no_clk, inouts_clk = partition(lambda v: v.name == 'clk', input)

    cycle = Vertex('cycle', types['const'])
    cycle.value = 0

    mon_verts = [cycle] + list(inouts_no_clk)
    disp_fmt = render_fmts(mon_verts, 's')
    disp_args = render_args(mon_verts, True)
    mon_fmt = render_fmts(mon_verts, None)
    mon_args = render_args(mon_verts, False)

    kw = {
        'mod_name' : mod_name,
        'tests' : tests,
        'io_groups' : io_groups,
        'inouts' : format_inouts(2, input, output),
        'disp_fmt' : disp_fmt,
        'disp_args' : disp_args,
        'mon_fmt' : mon_fmt,
        'mon_args' : mon_args,
        'has_clk' : list(inouts_clk)
    }
    render_tmpl_to_file('tb.v', path / f'{mod_name}_tb.v', **kw)
