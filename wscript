from pathlib import Path

def configure(ctx):
    ctx.env['IVERILOG'] = ctx.find_program('iverilog')

PATH_VERILOG = Path('verilog')
PATH_VERILOG_TB = PATH_VERILOG / 'tb'
PATH_VERILOG_LIB = PATH_VERILOG / 'lib'

def build_verilog_module(ctx, name):
    target = PATH_VERILOG_TB / name
    source = [PATH_VERILOG_TB / (name + '.sv'),
              PATH_VERILOG_LIB / (name + '.sv')]
    ctx(target = str(target),
        source = [str(s) for s in source],
        rule = '${IVERILOG} -g2012 -I ../verilog/lib ${SRC[0]} -o ${TGT}')

def build(ctx):
    build_verilog_module(ctx, 'counter')
    build_verilog_module(ctx, 'divider')
    build_verilog_module(ctx, 'matmul')
