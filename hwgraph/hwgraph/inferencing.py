# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from hwgraph.algebra import constrain

def infer(vars, expr):
    constraints = {}
    expr = subst(vars, expr)
    return constraints

def no_solution(vars, exprs):
    vs = ['%s == %s' % (n, v) for n, v in vars.items() if v is not None]
    fmt = 'No solution for system: %s'
    err = fmt % ', '.join(vs + exprs)
    raise ValueError(err)

def infer(v):
    tp = v.type

    input_wires = {n : v_in.output[pin]
                   for n, (v_in, pin) in zip(tp.input, v.input)}
    inputs = {n : w.arity for n, w in input_wires.items()}
    outputs = {n : w.arity for n, w in v.output.items()}

    orig_vars = dict(inputs)
    orig_vars.update(outputs)
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
            if var in outputs:
                v.output[var].arity = arity
            elif var in inputs:
                input_wires[var].arity = arity
            vars[var] = arity
        changed = True
    return changed

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
