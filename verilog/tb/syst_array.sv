/*
 A = [[15, 2, 3],
      [4, 5, 6],
      [7, 8, 9]]
 B = [[10, 11, 12],
      [13, 14, 15],
      [16, 17, 18]]
 */

`include "syst_array.sv"
module syst_array_tb();
    localparam WIDTH = 16;

    // Cycle counter
    reg [15:0] cycle;
    reg [0:0] clk, rstn;
    task tick; begin
        #5 clk = ~clk;
        cycle = cycle + 1;
        #5 clk = ~clk;
    end endtask

    // DUT input
    reg [0:0] in_valid;
    reg [WIDTH-1:0] b_col [0:2];
    reg [WIDTH-1:0] a_row [0:2];

    // DUT output
    logic [0:0] in_ready;
    logic [WIDTH-1:0] op0, op1, op2;

    initial begin
        $display("Running tests");

        $display("cycle rstn in_valid in_ready  o0  o1  o2");
        $monitor(
            "%5d %4b %8b %8b %3d %3d %3d",
            cycle, rstn,
            in_valid, in_ready,
            op0, op1, op2
        );


        cycle = 0;
        rstn = 0;
        clk = 0;
        in_valid = 0;
        tick;

        rstn = 1;
        in_valid = 1;

        // Cycle 0
        a_row[0] = 15; a_row[1] =  2; a_row[2] =  3;
        b_col[0] = 10; b_col[1] = 13; b_col[2] = 16;
        tick;

        // Cycle 1
        in_valid = 0;
        a_row[0] =  4; a_row[1] =  5; a_row[2] =  6;
        b_col[0] = 11; b_col[1] = 14; b_col[2] = 17;
        tick;

        // Cycle 2
        a_row[0] =  7; a_row[1] =  8; a_row[2] =  9;
        b_col[0] = 12; b_col[1] = 15; b_col[2] = 18;
        tick;

        a_row[0] = 0; a_row[1] = 0; a_row[2] = 0;
        b_col[0] = 0; b_col[1] = 0; b_col[2] = 0;

        // Cycle 3
        tick;

        assert(op0 == 244 && op1 == 224 && op2 == 201);

        // Cycle 4
        tick;
        assert(op0 == 264 && op1 == 216 && op2 == 318);

        // Cycle 5
        tick;
        assert(op0 == 231 && op1 == 216 && op2 == 342);

        // Cycle 6
        tick;
        assert(op0 == 366 && op1 == 366 && op2 == 366);

        // Cycle 7
        tick;

    end

    syst_array #(.WIDTH(WIDTH)) dut(
        clk, rstn,
        in_valid, in_ready,
        b_col,
        a_row,
        op0, op1, op2
    );


endmodule
