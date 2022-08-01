# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from hwgraph.types import TYPES

# All infix types with two inputs.
TYPES_BINARY = {
    TYPES['and'],
    TYPES['xor'],
    TYPES['or'],
    TYPES['ge'], TYPES['gt'],
    TYPES['le'],
    TYPES['shl'],
    TYPES['eq'],
    TYPES['sub'],
    TYPES['add'],
    TYPES['mul']
}
# All ops with one input.
TYPES_UNARY = {
    TYPES['not'],
    TYPES['reduce_and'],
    TYPES['reduce_xor'],
    TYPES['reduce_or']
}

TYPE_SYMBOLS = {
    TYPES['and'] : '&',
    TYPES['xor'] : '^',
    TYPES['or'] : '|',
    TYPES['ge'] : '>=',
    TYPES['gt'] : '>',
    TYPES['le'] : '<=',
    TYPES['eq'] : '==',
    TYPES['shl'] : '<<',

    TYPES['sub'] : '-',
    TYPES['add'] : '+',
    TYPES['mul'] : '*',


    TYPES['not'] : '!',
    TYPES['reduce_xor'] : '^',
    TYPES['reduce_and'] : '&',
    TYPES['reduce_or'] : '|'
}

def package_expr(src, dst):
    src_tp = src.type
    dst_tp = dst and dst.type
    if src_tp in TYPES_BINARY | TYPES_UNARY:
        if dst_tp in TYPES_BINARY | TYPES_UNARY:
            return '(%s)'
    elif src_tp == TYPES['cat'] and dst_tp != TYPES['cat']:
        return '{%s}'
    return '%s'
