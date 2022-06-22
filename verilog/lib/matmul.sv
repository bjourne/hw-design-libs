// Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>

module divider #(parameter WIDTH=8) (
    input wire logic clk,
    input wire logic start
);
    always_ff @(posedge clk) begin
        if (start) begin
        end else if (busy) begin
        end
    end
endmodule
