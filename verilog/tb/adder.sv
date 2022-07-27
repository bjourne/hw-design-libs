`include "adder.sv"
module adder_tb();
    // Inputs
    reg [3:0] a, b;
    reg [0:0] ci;

    // Outputs
    wire [3:0] s;
    wire [0:0] co;

    // task tick; begin
    //     #5 clk = ~clk;
    //     #5 clk = ~clk;
    // end endtask

    initial begin
        $display(
            "%2s %2s %2s %2s %2s",
            "a", "b", "ci", "s", "co"
        );
        $monitor(
            "%2d %2d %2b %2d %2b",
            a, b, ci, s, co
        );


        a = 3;
        b = 3;
        ci = 0;

        #5;

        a = 7;

        #5;
        a = 15;
        b = 1;



        //tick;

    end

    adder dut (a, b, ci, s, co);

endmodule
