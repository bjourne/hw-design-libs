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
