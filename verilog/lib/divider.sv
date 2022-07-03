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
    typedef struct packed {
        logic [WIDTH - 1:0] q1;
        logic [WIDTH:0] ac;
    } regs_t;
    function regs_t next_regs(
        regs_t in,
        logic [WIDTH - 1:0] y1
    );
        if (in.ac >= y1) begin
            next_regs.q1 = (in.q1 << 1) | 1'b1;
            next_regs.ac = ((in.ac - y1) << 1) | in.q1[WIDTH - 1];
        end else begin
            next_regs.q1 = in.q1 << 1;
            next_regs.ac = (in.ac << 1) | in.q1[WIDTH - 1];
        end
    endfunction

    logic [WIDTH - 1:0] y1;
    logic [$clog2(WIDTH):0] i;
    regs_t curr;

    always_ff @(posedge clk) begin
        regs_t next;
        if (start) begin
            valid <= 0;
            i <= WIDTH - 1;
            y1 <= y;
            curr.ac <= x[WIDTH - 1];
            curr.q1 <= x << 1;
            if (y == 0) begin
                busy <= 0;
                dbz <= 1;
            end else begin
                busy <= 1;
                dbz <= 0;
            end
        end else if (busy) begin
            next = next_regs(curr, y1);
            if (i == 0) begin
                busy <= 0;
                valid <= 1;
                q <= next.q1;
                r <= next.ac[WIDTH:1];
            end else begin
                i <= i - 1;
                curr = next;
            end
        end
    end
endmodule
