// Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
`include "matmul.sv"
module matmul_tb();
    localparam WIDTH = 8;
    localparam BUF_SIZE = 100;
    reg signed [WIDTH - 1:0] mat_a [0:3];
    reg signed [WIDTH - 1:0] mat_b [0:3];

    initial begin
        $readmemh("verilog/tb/mat_01_02x02.mem", mat_a);
        $readmemh("verilog/tb/mat_01_02x02.mem", mat_b);
        for (integer i = 0; i < 4; i = i + 1)
            $display("mat_a[%d] %d", i, mat_a[i]);
    end

endmodule
