`include "gcd.sv"
module gcd_tb();
    localparam WIDTH = 8;

    // Inputs
    reg [0:0] clk, rstn, in_valid, out_valid;
    reg [WIDTH-1:0] a, b;

    // Outputs
    wire [0:0] in_ready;
    wire [WIDTH-1:0] o;

    task tick; begin
        #5 clk = ~clk;
        #5 clk = ~clk;
    end
    endtask

    initial begin
        $display(
            "%5s %5s %8s %8s %9s %4s %4s %4s",
            "clk", "rstn", "in_ready", "in_valid", "out_valid",
            "a", "b", "o");
        $monitor(
            "%5b %5b %8b %8b %9b %4d %4d %4d",
            clk, rstn, in_ready, in_valid, out_valid,
            a, b, o);
        rstn = 0;
        clk = 0;
        in_valid = 0;

        tick;
        rstn = 1;
        tick;
        in_valid = 1;
        a = 12;
        b = 4;
        assert(in_ready == 1);

        repeat (5) begin
            tick;
            in_valid = 0;
        end

        assert (out_valid == 1);
        assert (o == 4);

        tick;
        assert(in_ready == 1);
        a = 8;
        b = 3;
        in_valid = 1;
        repeat (9) begin
            tick;
            in_valid = 0;
        end
        assert (out_valid == 1);
        assert (o == 1);
    end
    gcd #(.WIDTH(WIDTH)) dut (
        clk, rstn, a, b, o, in_valid, in_ready, out_valid
    );
endmodule
