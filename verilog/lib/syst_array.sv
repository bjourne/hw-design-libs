// Copyright (C) 2022-2023 Björn A. Lindqvist <bjourne@gmail.com>
//
// Systolic array controller. How it works? See this excellent video:
// https://www.youtube.com/watch?v=vADVh1ogNo0
module syst_pe #(parameter WIDTH=8) (
    clk, rstn,
    w, nw, n,
    e, se, s
);
    input clk, rstn;
    input [WIDTH-1:0] w, nw, n;
    output logic [WIDTH-1:0] e, se, s;

    always_ff @(posedge clk) begin
        e <= w;
        s <= n;
        se <= nw + n * w;
    end
endmodule
module syst_array #(parameter WIDTH=8) (
    input [0:0] clk, rstn,
    input [0:0] in_valid,
    output [0:0] in_ready,
    input [WIDTH-1:0] b_col [0:2],
    input [WIDTH-1:0] a_row [0:2],

    // Icarus Verilog doesn't handle array output.
    output logic [WIDTH-1:0] op0,
    output logic [WIDTH-1:0] op1,
    output logic [WIDTH-1:0] op2
);
    // Process control
    logic [0:0] p;
    logic [3:0] cnt;

    assign in_ready = !p;
    wire [3:0] next_cnt = in_valid & in_ready ? 0 : cnt + 1;

    logic [WIDTH-1:0] row [0:4];
    logic [WIDTH-1:0] col [0:4];

    always_comb begin
        case (next_cnt)
          0: begin
              row[0] = a_row[0];
              row[1] = a_row[1];
              row[2] = a_row[2];
              row[3] = 0;
              row[4] = 0;

              col[0] = b_col[0];
              col[1] = b_col[1];
              col[2] = b_col[2];
              col[3] = 0;
              col[4] = 0;
          end
          1: begin
              row[0] = 0;
              row[1] = a_row[0];
              row[2] = a_row[1];
              row[3] = a_row[2];
              row[4] = 0;

              col[0] = 0;
              col[1] = b_col[0];
              col[2] = b_col[1];
              col[3] = b_col[2];
              col[4] = 0;
          end
          2: begin
              row[0] = 0;
              row[1] = 0;
              row[2] = a_row[0];
              row[3] = a_row[1];
              row[4] = a_row[2];

              col[0] = 0;
              col[1] = 0;
              col[2] = b_col[0];
              col[3] = b_col[1];
              col[4] = b_col[2];
          end
          4: begin
              // Output col12, col11, c21
              op0 = SE[3][4];
              op1 = SE[4][4];
              op2 = SE[4][3];
          end
          5: begin
              // Output col13, c22, c31
              op0 = SE[3][5];
              op1 = SE[4][4];
              op2 = SE[5][3];
          end
          6: begin
              // Output c23, c22, c32
              op0 = SE[4][5];
              op1 = SE[5][5];
              op2 = SE[5][4];
          end
          7: begin
              // Output c33
              op0 = SE[5][5];
              op1 = SE[5][5];
              op2 = SE[5][5];
          end
          default: begin
              row[0] = 0;
              row[1] = 0;
              row[2] = 0;
              row[3] = 0;
              row[4] = 0;

              col[0] = 0;
              col[1] = 0;
              col[2] = 0;
              col[3] = 0;
              col[4] = 0;

              op0 = 0;
              op1 = 0;
              op2 = 0;
          end
        endcase
    end

    always @(posedge clk) begin
        if (!rstn)
            p <= 0;
        else if (in_valid & in_ready)
            p <= 1;
        else if (cnt == 7)
            p <= 0;
        else
            p <= p;
        cnt <= next_cnt;
    end

    logic [WIDTH-1:0] E [4:0][5:0];
    logic [WIDTH-1:0] S [5:0][4:0];
    logic [WIDTH-1:0] SE [5:0][5:0];
    assign E[0][0] = row[0];
    assign E[1][0] = row[1];
    assign E[2][0] = row[2];
    assign E[3][0] = row[3];
    assign E[4][0] = row[4];

    assign S[0][0] = col[0];
    assign S[0][1] = col[1];
    assign S[0][2] = col[2];
    assign S[0][3] = col[3];
    assign S[0][4] = col[4];

    assign SE[0][0] = 0;
    assign SE[0][1] = 0;
    assign SE[0][2] = 0;
    assign SE[0][3] = 0;
    assign SE[0][4] = 0;
    assign SE[1][0] = 0;
    assign SE[2][0] = 0;
    assign SE[3][0] = 0;
    assign SE[4][0] = 0;

    generate
        for (genvar j = 0; j < 5; j++) begin
            for (genvar i = 0; i < 5; i++) begin
                syst_pe #(.WIDTH(WIDTH)) pe(
                    clk, rstn,
                    E[j][i],   SE[j][i], S[j][i],
                    E[j][i+1], SE[j+1][i+1], S[j+1][i]
                );
            end
        end
    endgenerate
endmodule
