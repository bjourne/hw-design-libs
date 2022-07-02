`include "divider.sv"
module divider_tb();
    localparam WIDTH = 8;

    reg clk, rst, start, busy, dbz;
    reg [WIDTH - 1:0] x, y;
    wire [WIDTH - 1:0] q, r;
    wire val;

    task tick; begin
        #5 clk = ~clk;
        #5 clk = ~clk;
    end
    endtask

    task automatic run_test(
        input logic [WIDTH - 1:0] x0,
        input logic [WIDTH - 1:0] y0,
        input logic [WIDTH - 1:0] q0,
        input logic [WIDTH - 1:0] r0
    ); begin
    end
        start = 1;
        x = x0;
        y = y0;
        tick;
        start = 0;
        repeat (WIDTH) tick;
        assert (q == q0);
        assert (r == r0);
        assert (val == 1);
    endtask


    initial begin
        $display ("time clk rst start  x  y  q  r val busy dbz");
        $monitor ("%3d    %b   %b     %b %3d %3d %3d %3d   %b    %b   %b",
  	          $time, clk, rst, start, x, y, q, r, val, busy, dbz);

        clk = 1;
        rst = 1;
        start = 0;
        tick;

        run_test(11, 3, 3, 2);

        start = 1;
        x = 10;
        y = 0;
        tick;
        assert (dbz == 1);
        assert (val == 0);

        run_test(55, 11, 5, 0);

        // We don't support negative numbers (yet).
        run_test(-8, -2, 0, 248);

        #5 $finish;
    end
    divider #(.WIDTH(WIDTH)) div (clk, start, busy, val, dbz, x, y, q, r);
endmodule
