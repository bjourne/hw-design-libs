def configure(ctx):
    ctx.env['IVERILOG'] = ctx.find_program('iverilog')

def build(ctx):
    ctx(target = 'verilog/tb/counter',
        source = 'verilog/tb/counter.sv',
        rule = '${IVERILOG} -g2012 -I ../verilog/lib ${SRC} -o ${TGT}')
    ctx(target = 'verilog/tb/divider',
        source = ['verilog/tb/divider.sv', 'verilog/lib/divider.sv'],
        rule = '${IVERILOG} -g2012 -I ../verilog/lib ${SRC[0]} -o ${TGT}')
