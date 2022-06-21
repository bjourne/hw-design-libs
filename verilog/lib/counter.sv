module counter (
    clk,
    rst,
    en,
    out
);
    input clk;
    input rst;
    input en;
    output [3:0] out;

    wire clk;
    wire rst;
    wire en;
    reg [3:0] out;

    always @ (posedge clk)
    begin
        if (rst == 1'b1) begin
            out <= 4'b0000;
        end
        else if (en == 1'b1) begin
            out <= out + 1;
        end
    end
endmodule
