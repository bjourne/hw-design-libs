# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from ast import *
from collections import Counter, defaultdict
from fractions import Fraction
from functools import reduce

def parse_expr(expr):
    return parse(expr).body[0].value

def multivariate(terms):
    return defaultdict(int, terms)

def multivariate_const(c):
    return multivariate({() : c})

def multivariate_name(id):
    return multivariate({((id, 1),) : 1})

def elwise(mv1, mv2, fun):
    combos = list(mv1) + list(mv2)
    return multivariate({c : fun(mv1[c], mv2[c]) for c in combos})

def add(mv1, mv2):
    return elwise(mv1, mv2, lambda x, y: x + y)

def sub(mv1, mv2):
    return elwise(mv1, mv2, lambda x, y: x - y)

def pow(mv1, mv2):
    assert len(mv2) == 1
    mv1_items = list(mv1.items())
    mv2_items = list(mv2.items())

    pows1, c1 = mv1_items[0]
    pows2, c2 = mv2_items[0]
    if c2 >= 1:
        # Distribute
        mv3 = multivariate_const(1)
        return reduce(lambda x, _: mul(x, mv1), range(c2), mv3)
    assert len(mv1) == 1
    if pows1 == ():
        return multivariate_const(Fraction(c1)**c2)
    assert False




def mul(mv1, mv2):
    mv3 = multivariate_const(0)
    for es1, c1 in mv1.items():
        for es2, c2 in mv2.items():
            es3 = Counter(dict(es1))
            es3.update(dict(es2))
            es3 = tuple(sorted(es3.items()))
            mv3[es3] += c1*c2
    return mv3

def div(mv1, mv2):
    return mul(mv1, pow(mv2, multivariate_const(-1)))

def lookup_id(vars, id):
    val = vars.get(id)
    if val is not None:
        return multivariate_const(val)
    return multivariate_name(id)

BINOPS = {
    Add : add, Sub : sub,
    Mult : mul, Div : div,
    Pow : pow
}

def eval(tree, vars):
    tp = type(tree)
    if tp == BinOp:
        l = eval(tree.left, vars)
        r = eval(tree.right, vars)
        return BINOPS[type(tree.op)](l, r)
    elif tp == Name:
        return lookup_id(vars, tree.id)
    elif tp == Constant:
        return multivariate_const(tree.value)
    elif tp == UnaryOp:
        a = eval(tree.operand, vars)
        return mul(a, multivariate_const(-1))
    elif tp == Attribute:
        id = '%s.%s' % (tree.value.id, tree.attr)
        return lookup_id(vars, id)
    else:
        print(dump(tree))
        assert False

def constrain2(mv, tp_op):
    by_var = defaultdict(lambda: defaultdict(int))
    for var_pows, c in mv.items():
        if c != 0:
            for v, p in var_pows:
                by_var[v][p] = c
    c_term = mv[()]

    n_vars = len(by_var)
    if n_vars == 0:
        if tp_op == Gt:
            if c_term > 0:
                return 'satisfies'
            else:
                return 'nosol'
        elif tp_op == Lt:
            if c_term < 0:
                return 'satisfies'
            else:
                return 'nosol'
        elif tp_op == Eq:
            if c_term == 0:
                return 'satisfies'
            else:
                return 'nosol'
    elif n_vars > 1:
        # Can't constrain multiple variables.
        return 'many'

    by_var = list(by_var.items())
    var, cs = by_var[0]
    cs[0] = c_term

    # Not sure about the sign stuff.
    p, q = -cs[0], cs[1]
    sp, sq = p < 0, q < 0
    rat = Fraction(p, q)
    symbols = {Gt : '>', GtE : '>=',
               Lt : '<', LtE : '<=',
               Eq : '=='}

    oppo = {Gt : Lt, GtE : LtE,
            Lt : Gt, LtE : GtE, Eq : Eq}
    if sq:
        tp_op = oppo[tp_op]

    return var, symbols[tp_op], rat

def constrain(vars, expr):
    tree = parse_expr(expr)
    lhs, op, rhs = tree.left, tree.ops[0], tree.comparators[0]
    tree = BinOp(lhs, Sub(), rhs)
    mv = eval(tree, vars)
    return constrain2(mv, type(op))

def main():
    vars = {'hi' : 20, 'o' : 10}
    res = constrain(vars, '(hi + o)/hi == o')

if __name__ == '__main__':
    main()
