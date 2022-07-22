// Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>

module gcd #(parameter WIDTH=16) (
    clk, rstn, a, b, o,
    in_valid, in_ready, out_valid
);
    input clk, rstn;
    input [WIDTH-1:0] a, b;
    input [0:0] in_valid;

    output [0:0] in_ready, out_valid;
    output [WIDTH-1:0] o;

    wire [0:0] not_rstn = !rstn;
    wire [0:0] not_p = !p;

    wire [0:0] begin_p = in_valid & not_p;

    wire [0:0] p_next3 = y_eq_0 ? 0 : p;
    wire [0:0] p_next2 = begin_p ? 1 : p_next3;
    wire [0:0] p_next = not_rstn ? 0 : p_next2;

    wire [0:0] in_ready = not_p;

    wire [0:0] x_ge_y = x > y;
    wire [0:0] y_eq_0 = y == 0;
    wire [WIDTH-1:0] y_sub_x = y - x;

    wire [2*WIDTH-1:0] next3 = x_ge_y ? {y, x} : {x, y_sub_x};
    wire [2*WIDTH-1:0] next2 = p ? next3 : {x, y};
    wire [2*WIDTH-1:0] next = begin_p ? {a, b} : next2;

    wire [0:0] out_valid = y_eq_0 & p;
    wire [WIDTH-1:0] o = x;

    reg [0:0] p;
    reg [WIDTH-1:0] x;
    reg [WIDTH-1:0] y;
    always_ff @(posedge clk) begin
        $display("p, x, y <= %d %d", p_next, next);
        p <= p_next;
        {x, y} <=   next;
    end
endmodule
