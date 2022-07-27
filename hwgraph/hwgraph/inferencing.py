# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from hwgraph.algebra import constrain

DEFAULT_INT_ARITY = 20

def no_solution(vars, exprs):
    vs = ['%s == %s' % (n, v) for n, v in vars.items() if v is not None]
    fmt = 'No solution for system: %s'
    err = fmt % ', '.join(vs + exprs)
    raise ValueError(err)

def infer_vertex(v):
    tp = v.type

    input_wires = {n : v_in.output[pin]
                   for n, (v_in, pin) in zip(tp.input, v.input)}
    input_arities = {n : w.arity for n, w in input_wires.items()}
    output_arities = {n : w.arity for n, w in v.output.items()}
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
                v.output[var].arity = arity
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

    # Special treatment of arguments to slice vertices.
    for v in vertices:
        if v.type.name == 'slice':
            for v_from, _ in v.input[1:]:
                wire = v_from.output['o']
                if wire.arity is not None:
                    continue
                dests = set(wire.destinations)
                if len(dests) == 1:
                    wire.arity = DEFAULT_INT_ARITY

    missing = []
    for v in vertices:
        for pin, w in v.output.items():
            if not w.arity:
                missing.append('%s.%s' % (v.name, pin))

    fmt = 'Cannot infer arities for %s. Explicit declaration necessary.'
    if missing:
        raise ValueError(fmt % ', '.join(missing))

def main():
    c1 = Vertex('c1', Type('const', [], ['o'], []))
    c1.output['o'].arity = 5
    v = Vertex('v', Type('cat', ['i1', 'i2'], ['o'],
                         ['i1 + i2 == o']))
    connect_vertices(c1, 'o', v)
    connect_vertices(c1, 'o', v)
    v.output['o'].arity = None
    print(forward(v))

if __name__ == '__main__':
    main()
