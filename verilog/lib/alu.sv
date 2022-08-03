// Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
module alu #(parameter WIDTH=8) (
    input [WIDTH-1:0] i1, i2,
    input [2:0] sel,
    output logic [WIDTH-1:0] o
);
    always_comb begin
        case (sel)
          3'd0:
              o = i1 + i2;
          3'd1:
              o = i1 - i2;
          default:
              o = i1 + i2;
        endcase
    end
endmodule
