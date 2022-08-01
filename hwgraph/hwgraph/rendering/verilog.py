# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from collections import defaultdict
from hwgraph import Vertex
from hwgraph.rendering import (TYPES_BINARY, TYPE_SYMBOLS, TYPES_UNARY,
                               package_expr)
from hwgraph.types import TYPES
from hwgraph.utils import BASE_INDENT, flatten, groupby_sort
from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template
from more_itertools import partition
from pathlib import Path

TMPL_PATH = Path(__file__).parent / 'templates'
ENV = Environment(loader = FileSystemLoader(TMPL_PATH),
                  undefined = StrictUndefined)
def render_tmpl_to_file(tmpl_name, file_path, **kwargs):
    tmpl = ENV.get_template(tmpl_name)
    txt = tmpl.render(**kwargs)
    with open(file_path, 'wt') as of:
        of.write(txt + '\n')

def render_lval(lval_tp, v):
    return f'{lval_tp} [{v.output[0].arity - 1}:0] {v.name}'

def arg_needs_width(dst):
    tp = dst.type
    return tp.is_module or tp == TYPES['cat']

def input_wire_name(v, pin):
    tp = v.type
    if len(v.output) == 1 and not tp.is_module:
        return v.name
    return '%s_%s' % (v.name, tp.output[pin])

def render_arg(src, pin, dst):
    if (src.refer_by_name or
        src.type in {TYPES['if'], TYPES['reg']} or
        src.type.is_module):
        return input_wire_name(src, pin)
    return render_rval(src, pin, dst)

def render_rval(src, pin, dst):
    tp = src.type.name

    args = tuple([render_arg(v, pin, src) for v, pin in src.input])
    sym = TYPE_SYMBOLS.get(src.type)

    if src.type.is_module:
        return ', '.join(args)
    elif src.type in TYPES_BINARY:
        s = '%s %s %s' % (args[0], sym, args[1])
        return package_expr(src, dst) % s
    elif src.type == TYPES['cat']:
        s = '%s, %s' % args
        return package_expr(src, dst) % s
    elif tp == 'cast':
        return "%s'(%s)" % args
    elif src.type in TYPES_UNARY:
        s = '%s%s' % (sym, args[0])
        return package_expr(src, dst) % s
    elif src.type.name in {'input', 'reg'}:
        return src.name
    if src.type == TYPES['const']:
        wire = src.output[0]
        if arg_needs_width(dst):
            return "%s'd%s" % (wire.arity, wire.value)
        return '%s' % wire.value
    elif tp == 'slice':
        return '%s[%s:%s]' % args
    elif tp == 'if':
        fmt = '%s ? %s : %s'
        if max(len(a) for a in args) > 14:
            s = '\n' + ' ' * BASE_INDENT * 2
            fmt = s.join(['%s', '? %s', ': %s'])
        return fmt % args
    elif tp == 'output':
        return args[0]
    else:
        print(tp)
        assert False

ENV.globals.update(zip = zip,
                   render_rval = render_rval,
                   render_lval = render_lval)

def output_name(v1, pin_idx):
    wire = v1.output[pin_idx]
    dests = wire.destinations
    if len(dests) == 1:
        v2 = dests[0]
        if v2.type.name == 'output':
            return v2.name, False, None
    name = '%s_%s' % (v1.name, v1.type.output[pin_idx])
    return name, True, wire.arity

def render_submod_args(v):
    # Hackish
    input = render_rval(v, 0, None)

    output = [output_name(v, i) for i in range(len(v.output))]
    new_wires = [(n, a) for (n, new, a) in output if new]
    output = ', '.join(n for n, _, _ in output)

    if output:
        input += ', '
    return input + output, new_wires

def vertex_arity(v):
    tp = v.type.name
    if tp in {'input', 'const'}:
        return v.output[0].arity
    elif tp == 'output':
        v, pin = v.input[0]
        return v.output[0].arity
    assert False

def group_inputs_and_outputs(partitions, input_tp, output_tp):
    gr_ins = groupby_sort(partitions['input'], vertex_arity)
    gr_outs = groupby_sort(partitions['output'], vertex_arity)
    return [(input_tp, gr_ins), (output_tp, gr_outs)]

def format_inouts(n, input, output):
    input = ', '.join(v.name for v in input)
    output = ', '.join(v.name for v in output)
    if input and output:
        return input + ',\n' + ' ' * n * BASE_INDENT + output
    return input + output

def partition_vertices(vertices):
    partitions = defaultdict(list)
    for v in vertices:
        tp = v.type
        if tp == TYPES['input']:
            key = 'input'
        elif tp == TYPES['output']:
            key = 'output'
        elif tp == TYPES['reg']:
            key = 'reg'
        elif tp.is_module:
            key = 'submod'
        elif v.refer_by_name:
            key = 'explicit'
        elif tp == TYPES['if']:
            key = 'if'
        else:
            key = 'other'
        partitions[key].append(v)
    return partitions

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

def render_module(vertices, mod_name, path):
    partitions = partition_vertices(vertices)

    io_groups = \
        group_inputs_and_outputs(partitions, 'input', 'output')

    # Group registers by driving clock.
    regs = partitions['reg']
    regs_per_clk = groupby_sort(regs, lambda v: v.input[0][0].name)

    submods = partitions['submod']

    input = partitions['input']
    output = partitions['output']
    submod_names = sorted({v.type.name for v in submods if v.type.is_module})

    output_exprs = list(output)
    for submod in submods:
        for wire in submod.output:
            for dst in wire.destinations:
                if dst in output_exprs:
                    output_exprs.remove(dst)
    submods = [(v, render_submod_args(v)) for v in submods]

    kwargs = {
        'mod_name' : mod_name,
        'inouts' : format_inouts(1, input, output),
        'io_groups' : io_groups,
        'partitions' : partitions,
        'regs_per_clk' : regs_per_clk,
        'submod_names' : submod_names,
        'submods' : submods,
        'output_exprs' : output_exprs
    }
    render_tmpl_to_file('module.v', path / 'impl.v', **kwargs)

def render_tb(vertices, tests, mod_name, path):
    partitions = partition_vertices(vertices)
    io_groups = \
        group_inputs_and_outputs(partitions, 'reg', 'wire')

    input = partitions['input']
    output = partitions['output']

    input_no_clk, input_clk = partition(lambda v: v.name == 'clk', input)

    cycle = Vertex('cycle', TYPES['const'])
    cycle.value = 0

    mon_verts = [cycle] + list(input_no_clk) + output
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
        'has_clk' : len(list(input_clk)) > 0
    }
    render_tmpl_to_file('tb.v', path / 'tb.v', **kw)
