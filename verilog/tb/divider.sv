`include "divider.sv"
module divider_tb();
    localparam WIDTH = 8;

    reg clk, nrst, in_valid, dbz;
    reg [WIDTH - 1:0] x, y;
    wire [WIDTH - 1:0] q, r;
    wire out_valid;
    wire in_ready;

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
        in_valid = 1;
        x = x0;
        y = y0;
        repeat (WIDTH+1) tick;
        assert (q == q0);
        assert (r == r0);
        assert (out_valid == 1);
    endtask


    initial begin
        $display("%4s %3s %4s %8s %3s %3s %3s %3s %9s %8s %3s",
            "time", "clk", "nrst", "in_valid",
            "x", "y", "q", "r",
            "out_valid", "in_ready", "dbz");
        $monitor (
            "%4d %3b %4b %8b %3d %3d %3d %3d %9b %8b %3b",
  	    $time, clk, nrst, in_valid, x, y, q, r,
            out_valid, in_ready, dbz);

        clk = 1;
        nrst = 0;
        in_valid = 0;
        tick;

        nrst = 1;
        tick;

        assert(in_ready == 1);
        in_valid = 1;
        x = 128;
        y = 128;
        repeat(WIDTH+2) tick;
        assert(out_valid == 1);
        assert(q == 1 && r == 0);
        tick;

        in_valid = 1;
        x = 10;
        y = 10;
        tick;
        assert(in_ready == 0);
        assert(dbz == 0);

        y = 0;
        tick;
        assert(dbz == 0);

        // Reset.
        nrst = 0;
        tick;
        nrst = 1;

        // Cannot affect the computation by changing x or y.
        in_valid = 1;
        x = 10;
        y = 5;
        repeat (WIDTH+1) tick;
        assert (q == 2);
        assert (r == 0);
        assert (out_valid == 1);

        // Reset.
        nrst = 0;
        tick;
        nrst = 1;

        run_test(11, 3, 3, 2);

        in_valid = 1;
        x = 10;
        y = 0;
        tick;
        assert (dbz == 1);
        assert (out_valid == 0);

        run_test(55, 11, 5, 0);

        tick;

        // We don't support negative numbers (yet).
        run_test(-8, -2, 0, 248);

        #5 $finish;
    end
    divider #(.WIDTH(WIDTH)) div (
        .clk(clk),
        .nrst(nrst),
        .in_valid(in_valid),
        .in_ready(in_ready),
        .out_valid(out_valid),
        .dbz(dbz),
        .x(x),
        .y(y),
        .q(q),
        .r(r)
    );
endmodule
