# Copyright (C) 2022-2023 Björn A. Lindqvist <bjourne@gmail.com>
from pathlib import Path
from subprocess import check_output

def configure(ctx):
    ctx.env['IVERILOG'] = ctx.find_program('iverilog')
    ctx.env['GHDL'] = ctx.find_program('ghdl')
    ctx.env['VERILATOR'] = ctx.find_program('verilator')
    ctx.env['MAKE'] = ctx.find_program('make')

    o = check_output([ctx.env['GHDL'][0], '--version'])
    s = o.decode('utf-8').splitlines()[2]
    obj_gen = not 'mcode' in s
    ctx.env['GHDL_OBJ_GEN'] = obj_gen

PATH_VERILOG = Path('verilog')
PATH_VERILOG_TB = PATH_VERILOG / 'tb'
PATH_VERILOG_LIB = PATH_VERILOG / 'lib'

PATH_VHDL = Path('vhdl')
PATH_VHDL_TB = PATH_VHDL / 'tb'
PATH_VHDL_LIB = PATH_VHDL / 'lib'

def build_verilog_module(ctx, name):
    target = Path('iverilog') / name
    tb_src = PATH_VERILOG_TB / (name + '.sv')
    lib_src = PATH_VERILOG_LIB / (name + '.sv')
    source = [tb_src, lib_src]
    ctx(target = str(target),
        source = [str(s) for s in source],
        rule = '${IVERILOG} -g2012 -I ../verilog/lib ${SRC[0]} -o ${TGT}')

def build_verilator_tb(ctx, name):
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

def vhdl_analyze(ctx, vhdl_files, target_lib, use_lib):
    rule_fmt = 'rm -f ${TGT} && ${GHDL} -a --work=%s --std=08 %s'
    source = ' '.join(str(Path('..') / f) for f in vhdl_files)
    rule = rule_fmt % (target_lib, source)
    vhdl_source = list(map(str, vhdl_files))
    if use_lib:
        vhdl_source += ['%s-obj08.cf' % use_lib]
    ctx(target = '%s-obj08.cf' % target_lib,
        source = vhdl_source,
        rule = rule)

def build_vhdl_objs(ctx, source, lib_name):
    # Really annoying hackish hacks.
    lib_file = '%s-obj08.cf' % lib_name
    target = [f'{s.stem}.o' for s in source]
    rule = '${GHDL} -a --std=08 %s' % ' '.join(
        str(Path('..') / s) for s in source)
    ctx(target = target,
        source = list(map(str, source)) + [lib_file],
        rule = rule)

def build_vhdl_tb(ctx, tb_name, lib_name):
    source = [PATH_VHDL_TB / f'{tb_name}.vhdl',
              '%s-obj08.cf' % lib_name,
              '%s.o' % tb_name]
    target = PATH_VHDL_TB / tb_name
    rule = '${GHDL} -e --std=08 -o ${TGT} %s' % tb_name
    ctx(target = str(target),
        source = map(str, source),
        rule = rule)

def build(ctx):
    build_verilog_module(ctx, 'counter')
    build_verilog_module(ctx, 'divider')
    build_verilog_module(ctx, 'gcd')
    build_verilog_module(ctx, 'matmul')
    build_verilog_module(ctx, 'full_adder')
    build_verilog_module(ctx, 'adder')
    build_verilog_module(ctx, 'alu')
    build_verilog_module(ctx, 'syst_array')
    build_verilator_tb(ctx, 'matmul')

    # GHDL stuff
    vhdl_lib_files = [
        'math.vhdl',
        'types.vhdl',
        'utils.vhdl',
        'invsqrt_f32.vhdl',
        'io.vhdl',
        'dct8.vhdl',
        'dct8x8.vhdl',
        'parity.vhdl',
        'systolic.vhdl',
        'dp_bram.vhdl',
        'full_adder.vhdl',
        'half_adder.vhdl',
        'wallace_tree.vhdl',
        'ieee754.vhdl',
    ]
    vhdl_lib_files = [PATH_VHDL_LIB / n for n in vhdl_lib_files]
    vhdl_tb_files = list(PATH_VHDL_TB.glob('*.vhdl'))

    # Not sure how vhdl packages work.
    vhdl_analyze(ctx, vhdl_lib_files, 'bjourne', None)
    if ctx.env['GHDL_OBJ_GEN']:
        build_vhdl_objs(ctx, vhdl_tb_files, 'bjourne')
        for tb in vhdl_tb_files:
            build_vhdl_tb(ctx, tb.stem, 'bjourne')
    else:
        vhdl_analyze(ctx, vhdl_tb_files, 'work', 'bjourne')
