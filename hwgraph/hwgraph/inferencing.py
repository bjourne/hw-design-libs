# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from hwgraph import UNARY_OPS

COMPARE_OPS = {'ge', 'gt', 'eq'}
ARITH_OPS = {'and', 'xor', 'or', 'sub', 'add'}

def input_arities(v):
    return [v_in.output[pin].arity for (v_in, pin) in v.input]

def ensure(v, pin, arity):
    o = v.output[pin]
    if o.arity == arity:
        return False
    elif o.arity is None:
        o.arity = arity
        return True
    print(v, arity)
    print("%s incompatible with arity %d." % (v, arity))
    assert False

OPS = {
    "add" : lambda x, y: x + y
}

def evaluate(vars, expr):
    if type(expr) == str:
        return vars[expr]
    op, lhs, rhs = expr

    lhs = evaluate(vars, lhs)
    rhs = evaluate(vars, rhs)

    if lhs is not None and rhs is not None:
        return OPS[op](lhs, rhs)
    return None

def subst(vars, expr):
    tp = type(expr)
    if tp == list:
        return [expr[0], subst(vars, expr[1]), subst(vars, expr[2])]
    elif tp == str and vars[expr] is not None:
        return vars[expr]
    else:
        return expr

def infer_expr(vars, expr):
    constraints = {}

    expr = subst(vars, expr)
    print(expr)

    return constraints

def infer(vars, exprs):
    constraints = {}
    for expr in exprs:
        constraints.update(infer_expr(vars, expr))
    return constraints

def forward(v):
    tp = v.type.name
    arities = input_arities(v)

    # Dubious
    if tp in {'if', 'reg'}:
        arities = arities[1:]
        ps = ps[1:]

    if tp == 'cat':
        if all(arities):
            return ensure(v, 'o', sum(arities))
    elif tp == 'cast':
        return ensure(v, ps[0].value)
    elif tp == 'slice':
        hi = int(ps[1].value)
        lo = int(ps[2].value)
        return ensure(v, hi - lo + 1)
    elif tp in {'if', 'reg'} | ARITH_OPS | UNARY_OPS:
        if len(set(arities)) == 1 and arities[0]:
            return ensure(v, 'o', arities[0])
    elif tp in COMPARE_OPS:
        return ensure(v, 1)
    return False



from hwgraph import *

def main():
    test1 = infer({"i1" : 5, "i2" : 9, "o" : None},
                  [["equals", ["add", "i1", "i2"], "o"]])
    print(test1)
    test2 = infer({"i1" : None, "i2" : 9, "o" : 15},
                  [["equals", ["add", "i1", "i2"], "o"]])
    print(test2)

if __name__ == '__main__':
    main()
