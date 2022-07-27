module full_adder (a, b, ci, s, co);
    input [0:0] a, b, ci;
    output [0:0] co, s;

    // Output wires
    wire [0:0] co = ((a ^ b) & ci) | (a & b);
    wire [0:0] s = (a ^ b) ^ ci;
endmodule
