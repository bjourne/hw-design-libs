// Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
typedef enum {
    IDLE, READ, CALCULATE, WRITE, ERROR
} matmul_state_t;
typedef struct packed {
    int rows;
    int cols;
} matmul_dims_t;
function int max(int a, int b);
    return a > b ? a: b;
endfunction
function int matmul_compute_time(
    matmul_dims_t a,
    matmul_dims_t b);
    return a.rows * ((b.rows + 1) * b.cols + 1) + 1;
endfunction
function int matmul_read_time(
    matmul_dims_t a,
    matmul_dims_t b);
    return max(a.rows * a.cols, b.rows * b.cols);
endfunction



module matmul #(parameter BUF_SIZE=1024) (
    input wire logic clk,
    input wire logic start,
    output     matmul_state_t state,
    input wire matmul_dims_t dims_a,
    input wire int in_a,
    input wire matmul_dims_t dims_b,
    input wire int in_b,
    output int out_c
);
    reg int cnt_a, cnt_b, cnt_c;
    reg int idx_a, idx_b, idx_c;
    reg int data_a [0:BUF_SIZE - 1];
    reg int data_b [0:BUF_SIZE - 1];
    reg int data_c [0:BUF_SIZE - 1];

    // Iteration variables used during calculation.
    reg int idx_i, idx_j, idx_k, mac;

    always_ff @(posedge clk) begin
        // Local variables
        reg int a_ik, b_kj;
        if (start) begin
            if (dims_a.rows * dims_a.cols < BUF_SIZE &&
                dims_b.rows * dims_a.cols < BUF_SIZE &&
                dims_a.cols == dims_b.rows) begin
                state <= READ;
                cnt_a <= dims_a.cols * dims_a.rows;
                cnt_b <= dims_b.cols * dims_b.rows;
                cnt_c <= dims_a.rows * dims_b.cols;
                idx_a <= 0;
                idx_b <= 0;
                idx_c <= 0;
            end else begin
                state <= ERROR;
            end
        end else begin
            if (state == READ) begin
                if (idx_a < cnt_a) begin
                    data_a[idx_a] <= in_a;
                    idx_a <= idx_a + 1;
                end
                if (idx_b < cnt_b) begin
                    data_b[idx_b] <= in_b;
                    idx_b <= idx_b + 1;
                end
                if (idx_a == cnt_a - 1 && idx_b == cnt_b - 1) begin
                    state <= CALCULATE;
                    idx_i <= 0;
                    idx_j <= 0;
                    idx_k <= 0;
                    mac <= 0;
                end
            end else if (state == ERROR) begin
                state <= IDLE;
            end else if (state == CALCULATE) begin
                if (idx_i == dims_a.rows) begin
                    state <= WRITE;
                    idx_c <= 0;
                end else begin
                    if (idx_j == dims_b.cols) begin
                        idx_j <= 0;
                        idx_i <= idx_i + 1;
                    end else begin
                        // This part could be optimized.
                        if (idx_k == dims_b.rows) begin
                            data_c[idx_i * dims_b.cols + idx_j] <= mac;
                            idx_j <= idx_j + 1;
                            idx_k <= 0;
                            mac <= 0;
                        end else begin
                            a_ik = data_a[idx_i * dims_a.cols + idx_k];
                            b_kj = data_b[idx_k * dims_b.cols + idx_j];
                            mac <= mac + a_ik * b_kj;
                            idx_k <= idx_k + 1;
                        end
                    end
                end
            end else if (state == WRITE) begin
                if (idx_c < cnt_c) begin
                    out_c <= data_c[idx_c];
                    idx_c <= idx_c + 1;
                end else begin
                    state <= IDLE;
                end
            end
        end
    end
endmodule
