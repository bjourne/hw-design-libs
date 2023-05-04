// Copyright (C) 2022-2023 Björn A. Lindqvist <bjourne@gmail.com>
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
    reg [2*WIDTH:0] acq;
    reg [WIDTH - 1:0] y1;
    reg [$clog2(WIDTH):0] i;
    reg [0:0] p;

    wire begin_p = in_valid & in_ready;
    wire [WIDTH:0] ac_sub_y1 = acq[2*WIDTH:WIDTH] - y1;

    // Outputs
    assign in_ready = !p;
    assign out_valid = p & (i == 0);
    assign dbz = begin_p & (y == 0);

    // This is wrong because it is delayed one cycle.
    assign r = acq[2*WIDTH:WIDTH+1];
    assign q = acq[WIDTH-1:0];

    always @(posedge clk) begin
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

        if (begin_p) begin
            acq <= {{WIDTH{1'b0}}, x, 1'b0};
        end else if (acq[2*WIDTH:WIDTH] >= y1)
            acq <= {ac_sub_y1[WIDTH-1:0], acq[WIDTH-1:0], 1'b1};
        else begin
            acq <= acq << 1;
        end
    end
endmodule
