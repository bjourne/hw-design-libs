// Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
//
// This module is an adaptation of
// https://github.com/projf/projf-explore/blob/main/lib/maths/div_int.sv
module divider #(parameter WIDTH=4) (
    input wire clk,
    input wire nrst,
    input wire in_valid,
    output in_ready,
    output out_valid,
    input wire [WIDTH-1:0] x,
    input wire [WIDTH-1:0] y,
    output [WIDTH-1:0] q,
    output [WIDTH-1:0] r,
    output dbz
);
    reg [WIDTH - 1:0] y1, q;
    reg [$clog2(WIDTH):0] i;
    reg [WIDTH:0] ac;
    reg [0:0] p;

    wire begin_p = in_valid & in_ready;
    wire [WIDTH:0] ac_sub_y1 = ac - y1;

    // Outputs
    wire in_ready = !p;
    wire out_valid = p & (i == 0);
    wire [WIDTH-1:0] r = ac[WIDTH:1];
    wire dbz = begin_p & (y == 0);

    always @(posedge clk) begin
        // State trans for p
        if (!nrst)
            p <= 0;
        else if (begin_p)
            p <= y != 0;
        else if (i == 0)
            p <= 0;
        else
            p <= p;

        // For y1 and i
        y1 <= begin_p ? y : y1;
        i <= begin_p ? WIDTH : i - 1;

        if (begin_p)
            {ac, q} <= {{WIDTH{1'b0}}, x, 1'b0};
        else if (ac >= y1)
            {ac, q} <= {ac_sub_y1[WIDTH-1:0], q, 1'b1};
        else
            {ac, q} <= {ac, q} << 1;
    end
endmodule
