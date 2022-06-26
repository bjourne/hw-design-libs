// Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
#include <stdlib.h>
#include <iostream>
#include <verilated.h>
#include <verilated_vcd_c.h>
#include "Vmatmul.h"
#include "Vmatmul___024unit.h"

#define MAX_SIM_TIME 20
vluint64_t sim_time = 0;

int main(int argc, char** argv, char** env) {
    Vmatmul *dut = new Vmatmul;

    dut->clk = 0;
    dut->eval();
    assert(dut->state == Vmatmul___024unit::matmul_state_t::IDLE);

    dut->start = 1;
    dut->dims_a = 0;
    dut->dims_b = 0;

    dut->clk = 1;
    dut->eval();
    assert(dut->state == Vmatmul___024unit::matmul_state_t::ERROR);

    dut->start = 0;
    dut->clk = 0;
    dut->eval();
    assert(dut->state == Vmatmul___024unit::matmul_state_t::ERROR);

    dut->clk = 1;
    dut->eval();
    assert(dut->state == Vmatmul___024unit::matmul_state_t::IDLE);

    delete dut;
    exit(EXIT_SUCCESS);
}
