// Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
`include "alu.sv"
module alu_tb();
    reg [7:0] i1, i2;
    reg [2:0] sel;
    wire [7:0] o;

    alu #(.WIDTH(8)) dut(i1, i2, sel, o);
endmodule
