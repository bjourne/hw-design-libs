# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from hwgraph import Vertex, connect_vertices
from hwgraph.types import TYPES
from hwgraph.rendering import package_expr
from hwgraph.rendering.verilog import (arg_needs_width,
                                       render_arg, render_lval, render_rval)

def const_with_value(val):
    v = Vertex('c', TYPES['const'])
    v.output[0].value = val
    return v

def test_render_lval():
    v = Vertex('c1', TYPES['const'])
    v.output[0].arity = 10
    s = render_lval('wire', v)
    assert s == 'wire [9:0] c1'

def test_render_if_arg():
    v = Vertex('v', TYPES['if'])
    assert render_arg(v, 0, None) == 'v'

def test_render_module_arg():
    v = Vertex('v', TYPES['full_adder'])
    v.refer_by_name = True
    assert render_arg(v, 0, None) == 'v_s'

def test_needs_width():
    v = Vertex('fa', TYPES['full_adder'])
    assert arg_needs_width(v)

def test_render_rval():
    v = Vertex('fa', TYPES['full_adder'])
    consts = [Vertex('c', TYPES['const']) for _ in range(3)]
    for i, c in enumerate(consts):
        wire = c.output[0]
        wire.value = i
        wire.arity = i
        connect_vertices(c, 0, v)
    assert render_rval(v, 0, None) == "0'd0, 1'd1, 2'd2"

def test_pack_cat():
    src = Vertex('s', TYPES['cat'])
    dst = Vertex('s', TYPES['if'])
    assert package_expr(src, dst) == '{%s}'
