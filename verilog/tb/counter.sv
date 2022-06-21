`include "counter.sv"
module counter_tb();
    reg clk, rst, en;

    wire [3:0] out;
    initial begin
        $display ("time clk rst en  cnt");
        $monitor ("%3d    %b   %b  %b   %d",
  	          $time, clk, rst, en, out);

        clk =  1;
        rst = 1;
        en = 1;
        #5 clk = ~clk;
        #5 clk = ~clk;
        rst = 0;
        assert (out == 0);
        #5 clk = ~clk;
        #5 clk = ~clk;
        assert (out == 1);
        #5 clk = ~clk;
        #5 clk = ~clk;
        assert (out == 2);

        repeat (20) #1 clk = ~clk;

        assert (out == 12);

        repeat (20) #1 clk = ~clk;

        assert (out == 6);


        #5 $finish;
    end
    counter U_counter (clk, rst, en, out);
endmodule
