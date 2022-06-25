// Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
`include "matmul.sv"

module matmul_tb();
    localparam BUF_SIZE = 1000;

    // Matrix A
    reg int data_a [0:BUF_SIZE - 1];
    reg matmul_dims_t dims_a;
    reg int in_a, mat_a_els;

    // Matrix B
    reg int data_b [0:BUF_SIZE - 1];
    reg matmul_dims_t dims_b;
    reg int in_b, mat_b_els;

    // Matrix C
    reg int data_c [0:BUF_SIZE - 1];
    reg matmul_dims_t dims_c;
    reg int out_c, mat_c_els;

    // General control
    reg clk, start;

    wire matmul_state_t state;

    task tick; begin
        #5 clk = ~clk;
        #5 clk = ~clk;
    end
    endtask

    // Copy paste cause I can't figure out how to pass array
    // references.
    task automatic read_matrices(
        input string name_a,
        input string name_b,
        input string name_c
    ); begin
        int r, f;
        f = $fopen(name_a, "rb");
        r = $fscanf(f, "%d", dims_a.rows);
        r = $fscanf(f, "%d", dims_a.cols);
        for (int i = 0; i < dims_a.rows * dims_a.cols; i++) begin
            r = $fscanf(f, "%d", data_a[i]);
        end
        $fclose(f);


        f = $fopen(name_b, "rb");
        r = $fscanf(f, "%d", dims_b.rows);
        r = $fscanf(f, "%d", dims_b.cols);
        for (int i = 0; i < dims_b.rows * dims_b.cols; i++) begin
            r = $fscanf(f, "%d", data_b[i]);
            assert(r == 1);
        end
        $fclose(f);

        f = $fopen(name_c, "rb");
        r = $fscanf(f, "%d", dims_c.rows);
        r = $fscanf(f, "%d", dims_c.cols);
        for (int i = 0; i < dims_c.rows * dims_c.cols; i++) begin
            r = $fscanf(f, "%d", data_c[i]);
            assert(r == 1);
        end
        $fclose(f);

        mat_a_els = dims_a.rows * dims_a.cols;
        mat_b_els = dims_b.rows * dims_b.cols;
        mat_c_els = dims_c.rows * dims_c.cols;
    end
    endtask

    task automatic assert_error; begin
        start = 1;
        tick;
        assert(state == ERROR);
        start = 0;
        tick;
        assert(state == IDLE);
    end
    endtask

    task automatic run_test(
        input string name_a,
        input string name_b,
        input string name_c
    ); begin
        read_matrices(name_a, name_b, name_c);
        start = 1;
        tick;

        assert(state == READ);
        start = 0;

        for (int i = 0;
             i < matmul_read_time(dims_a, dims_b);
             i = i + 1) begin
            if (i < mat_a_els) begin
                in_a = data_a[i];
            end
            if (i < mat_b_els) begin
                in_b = data_b[i];
            end
            tick;
        end
        assert(state == CALCULATE);

        repeat (matmul_compute_time(dims_a, dims_b))
            tick;

        assert(state == WRITE);
        for (int i = 0;
             i < matmul_write_time(dims_a, dims_b);
             i = i + 1) begin
            tick;
            assert(out_c == data_c[i]);
        end
        tick;
        assert(state == IDLE);
    end
    endtask

    initial begin
        $display(
            "time start state rows_a cols_a rows_b cols_b in_a in_b out_c"
        );
        $monitor(
            "%4d %5b %5d %6d %6d %6d %6d %4d %4d %5d",
            $time, start, state,
            dims_a.rows, dims_a.cols,
            dims_b.rows, dims_b.cols,
            in_a, in_b, out_c
        );

        clk = 1;
        start = 0;
        tick;

        // Too large.
        dims_a = {int'(1000), int'(1000)};
        dims_b = {int'(1000), int'(1000)};
        assert_error;

        // Dimension mismatch.
        dims_a = {int'(2), int'(3)};
        dims_b = {int'(4), int'(2)};
        assert_error;

        // Zeros
        dims_a = {int'(0), int'(10)};
        dims_b = {int'(10), int'(0)};
        assert_error;


        // Now for real
        run_test(
            "verilog/tb/mat_01_02x02.mem",
            "verilog/tb/mat_01_02x02.mem",
            "verilog/tb/mat_02_02x02.mem"
        );
        run_test(
            "verilog/tb/mat_03_16x16.mem",
            "verilog/tb/mat_04_16x16.mem",
            "verilog/tb/mat_05_16x16.mem"
        );
        #5 $finish;
    end

    matmul matmul (
        clk, start, state,
        dims_a, in_a,
        dims_b, in_b,
        out_c
    );
endmodule
