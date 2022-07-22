# hw-design-libs

This is a project in which I'm exploring various hardware description
languages (HDLs) by writing libraries and utilities.

Of the languages I have used so far, I like VHDL the
most. SystemVerilog is also nice but suffers from poor tooling support
on Linux. I don't like Verilator because you have to use C++ to write
testbenchs and Icarus Verilog doesn't support all SystemVerilog
features I want. Chisel is not bad, but I dislike having to use the
Scala Build Tool which feels slow and clunky. I agree with [Jan
Decaluwe's critique of
Chisel](https://www.jandecaluwe.com/blog/chisel-flawed-approach.html).

## Running testcases

If GHDL is built with mcode support:

    ghdl --elab-run -P./build --workdir=build --std=08 tb_<name_of_tb>

## HWGraph

A better way of designing hardware. Run it like this:

    cd hwgraph
    PYTHONPATH=. python hwgraph/run.py \
        examples/full_adder.json examples/full_adder_tb.json
    iverilog -g2012 output/test01_tb.v -Ioutput
    ./a.out
