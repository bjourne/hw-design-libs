// Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
//
// This module is an adaptation of
// https://github.com/projf/projf-explore/blob/main/lib/maths/div_int.sv

module divider #(parameter WIDTH=4) (
    input wire logic clk,
    input wire logic start,
    output     logic busy,
    output     logic valid,
    output     logic dbz,
    input wire logic [WIDTH-1:0] x,
    input wire logic [WIDTH-1:0] y,
    output     logic [WIDTH-1:0] q,
    output     logic [WIDTH-1:0] r
);
    logic [WIDTH - 1:0] y1;
    logic [$clog2(WIDTH):0] i;
    logic [WIDTH - 1:0] q1;
    logic [WIDTH:0] ac;

    always_ff @(posedge clk) begin
        logic [WIDTH - 1:0] q1_next;
        logic [WIDTH:0] ac_next;
        if (start) begin
            valid <= 0;
            i <= WIDTH - 1;
            y1 <= y;
            ac <= x[WIDTH - 1];
            q1 <= x << 1;
            if (y == 0) begin
                busy <= 0;
                dbz <= 1;
            end else begin
                busy <= 1;
                dbz <= 0;
            end
        end else if (busy) begin
            if (ac >= y1) begin
                q1_next = (q1 << 1) | 1'b1;
                ac_next = ((ac - y1) << 1) | q1[WIDTH - 1];
            end else begin
                q1_next = q1 << 1;
                ac_next = (ac << 1) | q1[WIDTH - 1];
            end
            if (i == 0) begin
                busy <= 0;
                valid <= 1;
                q <= q1_next;
                r <= ac_next[WIDTH:1];
            end else begin
                i <= i - 1;
                q1 <= q1_next;
                ac <= ac_next;
            end
        end
    end
endmodule
