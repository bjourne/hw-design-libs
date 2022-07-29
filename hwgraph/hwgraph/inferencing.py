# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
#from hwgraph import BASE_INDENT
from hwgraph.algebra import constrain
from hwgraph.utils import long_value_error

DEFAULT_INT_ARITY = 20

def no_solution(vars, exprs):
    lines = ['%s = %s' % nv for nv in vars.items() if nv[1] is not None]
    lines.extend(exprs)
    long_value_error('No solution for system:', lines)

def infer_vertex(v):
    tp = v.type

    input_wires = {n : v_in.output[pin]
                   for n, (v_in, pin) in zip(tp.input, v.input)}
    output_wires = {n : w for n, w in zip(tp.output, v.output)}

    input_arities = {n : w.arity for n, w in input_wires.items()}
    output_arities = {n : w.arity for n, w in output_wires.items()}
    input_values = {'%s.value' % n : w.value for n, w in input_wires.items()}

    orig_vars = dict(input_arities)
    orig_vars.update(output_arities)
    orig_vars.update(input_values)

    vars = dict(orig_vars)
    exprs = tp.constraints
    changed = False
    for expr in exprs:
        res = constrain(vars, expr)
        if res == 'nosol':
            no_solution(orig_vars, exprs)
        elif res in {'many', 'satisfies'}:
            continue
        var, op, arity = res
        if op == '==':
            if var in output_arities:
                output_wires[var].arity = arity
            elif var in input_arities:
                input_wires[var].arity = arity
            vars[var] = arity
            changed = True
    return changed

def infer_vertices(vertices):
    changed = True
    while changed:
        changed = False
        for v in vertices:
            changed = changed or infer_vertex(v)

    # Special treatment of arguments to slice and cast vertices.
    for v in vertices:
        const_args = []
        tp = v.type.name
        if tp == 'slice':
            const_args = v.input[1:]
        elif tp == 'cast':
            const_args = [v.input[0]]
        if not const_args:
            continue
        for v_from, _ in const_args:
            assert v_from.type.name == 'const'
            wire = v_from.output[0]
            if wire.arity is not None:
                continue
            if all(v.type.name in {'slice', 'cast'}
                   for v in wire.destinations):
                wire.arity = DEFAULT_INT_ARITY

    missing = []
    for src in vertices:
        for out_pin, w in enumerate(src.output):
            if w.arity is not None:
                continue
            dsts = w.destinations
            in_pins = [dst.input.index((src, out_pin))
                       for dst in dsts]

            in_ports = [(dst.name, dst.type.input[in_pin])
                        for in_pin, dst in zip(in_pins, dsts)]

            out_port = src.name, src.type.output[out_pin]
            missing.append((out_port, in_ports))

    missing = ['    %s.%s => %s' % (out_port[0], out_port[1],
                                    ', '.join('%s.%s' % in_port
                                              for in_port in in_ports))
               for out_port, in_ports in missing]

    err = ['Cannot infer arities for wires:',
           '\n'.join(missing),
           'Explicit declarations necessary.']
    if missing:
        raise ValueError('\n'.join(err))

def main():
    c1 = Vertex('c1', Type('const', [], ['o'], []))
    c1.output['o'].arity = 5
    v = Vertex('v', Type('cat', ['i1', 'i2'], ['o'],
                         ['i1 + i2 == o']))
    connect_vertices(c1, 'o', v)
    connect_vertices(c1, 'o', v)
    v.output['o'].arity = None

if __name__ == '__main__':
    main()
