# hw-design-libs
Libraries and utilities for hardware design that I have created

## Running testcases

If GHDL is built with mcode support:

    ghdl --elab-run -P./build --workdir=build --std=08 tb_<name_of_tb>
