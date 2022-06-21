`include "divider.sv"
module divider_tb();
    localparam WIDTH = 6;

    reg clk, rst, start, busy, dbz;
    reg [WIDTH - 1:0] x, y;
    wire [WIDTH - 1:0] q, r;
    wire val;

    task tick; begin
        #5 clk = ~clk;
        #5 clk = ~clk;
    end
    endtask

    initial begin
        $display ("time clk rst start  x  y  q  r val busy dbz");
        $monitor ("%3d    %b   %b     %b %2d %2d %2d %2d   %b    %b   %b",
  	          $time, clk, rst, start, x, y, q, r, val, busy, dbz);
        clk = 1;
        rst = 1;
        start = 0;

        tick;

        start = 1;
        x = 11;
        y = 3;
        tick;
        start = 0;

        repeat(WIDTH)
            tick;

        assert (q == 3);
        assert (r == 2);
        assert (val == 1);

        start = 1;
        x = 10;
        y = 0;
        tick;
        assert (dbz == 1);
        assert (val == 0);

        #5 $finish;
    end
    divider #(.WIDTH(WIDTH)) div (clk, start, busy, val, dbz, x, y, q, r);

endmodule
