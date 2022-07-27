`include "full_adder.sv"
module adder(a, b, ci, s, co);
    input [3:0] a, b;
    input [0:0] ci;
    output [3:0] s;
    output [0:0] co;

    wire c0, c1, c2;

    full_adder fa0 (a[0], b[0],  ci, s[0], co0);
    full_adder fa1 (a[1], b[1], co0, s[1], co1);
    full_adder fa2 (a[2], b[2], co1, s[2], co2);
    full_adder fa3 (a[3], b[3], co2, s[3],  co);
endmodule
