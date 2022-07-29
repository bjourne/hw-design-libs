from hwgraph import Type, Vertex, connect_vertices
from hwgraph.verilog import render_lval

TYPE_CAT = Type('cat',
                ['i1', 'i2'], ['o'], ['i1 + i2 == o'],
                False)
TYPE_ADD = Type('add',
                ['i1', 'i2'], ['o'], ['i1 == i2', 'i2 == o'],
                False)
TYPE_CONST = Type('const',
                  [], ['o'], [],
                  False)

def test_render_lval():
    v = Vertex('c1', TYPE_CONST)
    #s = render_lval('wire', v)
