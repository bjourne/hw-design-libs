# Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
from pathlib import Path

def configure(ctx):
    ctx.env['IVERILOG'] = ctx.find_program('iverilog')
    ctx.env['GHDL'] = ctx.find_program('ghdl')
    ctx.env['VERILATOR'] = ctx.find_program('verilator')
    ctx.env['MAKE'] = ctx.find_program('make')

PATH_VERILOG = Path('verilog')
PATH_VERILOG_TB = PATH_VERILOG / 'tb'
PATH_VERILOG_LIB = PATH_VERILOG / 'lib'

PATH_VHDL = Path('vhdl')
PATH_VHDL_TB = PATH_VHDL / 'tb'
PATH_VHDL_LIB = PATH_VHDL / 'lib'

def build_verilog_module(ctx, name):
    target = Path('iverilog') / name
    source = [PATH_VERILOG_TB / (name + '.sv'),
              PATH_VERILOG_LIB / (name + '.sv')]
    ctx(target = str(target),
        source = [str(s) for s in source],
        rule = '${IVERILOG} -g2012 -I ../verilog/lib ${SRC[0]} -o ${TGT}')

def build_verilator_testbench(ctx, name):
    dut_path = PATH_VERILOG_LIB / f'{name}.sv'
    tb_path = PATH_VERILOG_TB / f'tb_{name}.cpp'
    rule_fmt = ('${VERILATOR} --Mdir %s_dir --trace '
                '--cc ${SRC[0]} --exe ${SRC[1]} --build -o ../${TGT}')
    rule = rule_fmt % name

    target = Path('verilator') / name
    source = [dut_path, tb_path]
    ctx(target = str(target),
        source = map(str, source),
        rule = rule)

def build_vhdl_lib(ctx, source, lib_name):
    rule = '${GHDL} -a --std=08 --work=%s ${SRC}' % lib_name
    target = '%s-obj08.cf' % lib_name
    ctx(target = target,
        source = map(str, source),
        rule = rule)

def build_vhdl_tb(ctx, tb_name):
    source = PATH_VHDL_TB / f'{tb_name}.vhdl'
    target = PATH_VHDL_TB / tb_name

    rule = ' && '.join(['${GHDL} -a --std=08 ${SRC}',
                        '${GHDL} -e --std=08 %s' % tb_name,
                        'mv %s ${TGT}' % tb_name])
    ctx(target = str(target),
        source = str(source),
        rule = rule)

def build(ctx):
    build_verilog_module(ctx, 'counter')
    build_verilog_module(ctx, 'divider')
    build_verilog_module(ctx, 'matmul')
    build_verilator_testbench(ctx, 'matmul')
    build_vhdl_lib(ctx,
                   PATH_VHDL_LIB.glob('*.vhdl'),
                   'bjourne')
    build_vhdl_tb(ctx, 'tb_ieee754')
