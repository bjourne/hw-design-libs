from pathlib import Path

def configure(ctx):
    ctx.env['IVERILOG'] = ctx.find_program('iverilog')
    ctx.env['GHDL'] = ctx.find_program('ghdl')

PATH_VERILOG = Path('verilog')
PATH_VERILOG_TB = PATH_VERILOG / 'tb'
PATH_VERILOG_LIB = PATH_VERILOG / 'lib'

PATH_VHDL = Path('vhdl')
PATH_VHDL_TB = PATH_VHDL / 'tb'
PATH_VHDL_LIB = PATH_VHDL / 'lib'

def build_verilog_module(ctx, name):
    target = PATH_VERILOG_TB / name
    source = [PATH_VERILOG_TB / (name + '.sv'),
              PATH_VERILOG_LIB / (name + '.sv')]
    ctx(target = str(target),
        source = [str(s) for s in source],
        rule = '${IVERILOG} -g2012 -I ../verilog/lib ${SRC[0]} -o ${TGT}')

def build_vhdl_testbench(ctx, name):
    tb_name = f'tb_{name}'

    source = [PATH_VHDL_LIB / f'{name}.vhdl',
              PATH_VHDL_TB / f'{tb_name}.vhdl']
    target = PATH_VHDL_TB / tb_name

    # Best I can do
    rule = ' && '.join(['${GHDL} -a --std=08 ${SRC}',
                        '${GHDL} -e --std=08 %s' % tb_name,
                        'mv %s ${TGT}' % tb_name])
    ctx(target = str(target),
        source = map(str, source),
        rule = rule)

def build(ctx):
    build_verilog_module(ctx, 'counter')
    build_verilog_module(ctx, 'divider')
    build_verilog_module(ctx, 'matmul')
    build_vhdl_testbench(ctx, 'ieee754')
