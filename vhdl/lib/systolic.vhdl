-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;
use std.textio.all;

entity systolic is
    generic(
        N : integer
    );
    port(
        clk : in std_logic;
        rstn : in std_logic;
        in_valid : in std_logic;
        in_ready : out std_logic;
        a_row : in integer_vector(0 to N - 1);
        b_col : in integer_vector(0 to N - 1);
        c_row : out integer_vector(0 to N - 1)
    );
end entity;

architecture rtl of systolic is

    constant LAST : integer := 2*N - 1;

    type east_t is array(0 to LAST - 1, 0 to LAST) of integer;
    type south_t is array(0 to LAST, 0 to LAST - 1) of integer;
    type south_east_t is array(0 to LAST, 0 to LAST) of integer;
    type  buffer_t is array(0 to N, 0 to N - 2) of integer;

    signal cnt : natural;
    signal p : std_logic;

    signal E : east_t;
    signal S : south_t;
    signal SE : south_east_t;

    -- These buffers could be a problem for large Ns. :)
    --signal buf_col1 : integer_vector(0 to N - 2);
    --signal buf_col3 : integer_vector(0 to N - 4);
    --signal buf_col4 : integer_vector(0 to N - 5);
    -- signal buf_col5 : integer_vector(0 to N - 6);
    -- signal buf_col6 : integer_vector(0 to N - 7);

    signal buf : buffer_t;

    procedure report_systolic is
        variable fstatus : file_open_status;
        variable file_line : line;
        file fptr : text;
    begin
        -- write(file_line, string'("Tick #"));
        -- write(file_line, cnt);
        -- write(file_line, string'(" E:"));
        -- writeline(output, file_line);
        -- for r in 0 to LAST - 1 loop
        --     write(file_line, r, right, 3);
        --     for c in 0 to LAST loop
        --         write(file_line, E(r, c), right, 4);
        --     end loop;
        --     writeline(output, file_line);
        -- end loop;
        write(file_line, string'("Tick #"));
        write(file_line, cnt);
        write(file_line, string'(" SE:"));
        writeline(output, file_line);
        for r in 0 to LAST loop
            write(file_line, r, right, 3);
            for c in 0 to LAST loop
                write(file_line, SE(r, c), right, 4);
            end loop;
            writeline(output, file_line);
        end loop;
    end;
    procedure feed_data(cycle : integer;
                        signal row : integer_vector(0 to N - 1);
                        signal col : integer_vector(0 to N - 1);
                        signal E0 : out east_t;
                        signal S0 : out south_t) is
    begin
        for i in 0 to cycle - 1 loop
            E0(i, 0) <= 0;
            S0(0, i) <= 0;
        end loop;
        for i in cycle to cycle + N - 1 loop
            E0(i, 0) <= row(i - cycle);
            S0(0, i) <= col(i - cycle);
        end loop;
        for i in cycle + N to LAST - 1 loop
            E0(i, 0) <= 0;
            S0(0, i) <= 0;
        end loop;
    end;
begin
    process (clk, cnt, in_valid, in_ready, p)
        variable next_cnt : natural;
    begin

        -- Process control
        in_ready <= not p;
        if in_ready and in_valid then
            next_cnt := 0;
        elsif cnt = 3*N - 2 then
            next_cnt := 0;
        else
            next_cnt := cnt + 1;
        end if;
        if rising_edge(clk) then
            if rstn = '0' then
                p <= '0';
            elsif in_ready and in_valid then
                p <= '1';
            elsif cnt = 3*N - 3 then
                p <= '0';
            end if;
            cnt <= next_cnt;
        end if;

        -- Systolic array handling

        -- Input to the array.
        for i in 0 to LAST loop
            SE(0, i) <= 0;
            SE(i, 0) <= 0;
        end loop;
        feed_data(next_cnt rem N, a_row, b_col, E, S);

        -- Should be a case in the future.
        if next_cnt = LAST then
            for i in 0 to -1 loop
                c_row(i) <= buf(i, -1 - i);
            end loop;
            for i in 0 to N - 1 loop
                c_row(i) <= SE(LAST - i, LAST);
            end loop;
            -- Buffer c21, c31, ..., cN1
            for i in 0 to N - 2 loop
                buf(0, i) <= SE(LAST, LAST - 1 - i);
            end loop;
        elsif next_cnt = LAST + 1 then
            -- Buffered elements
            for i in 0 to 0 loop
                c_row(i) <= buf(i, 0 - i);
            end loop;
            -- Output c22, c23, ..., c2N
            for i in 1 to N - 1 loop
                c_row(i) <= SE(LAST - i + 1, LAST);
            end loop;
            -- Buffer c32, c42, ...
            for i in 0 to N - 3 loop
                buf(1, i) <= SE(LAST, LAST - 1 - i);
            end loop;
        elsif next_cnt = LAST + 2 then
            -- Output c31, c32
            for i in 0 to 1 loop
                c_row(i) <= buf(i, 1 - i);
            end loop;
            -- Output c33, c34
            for i in 2 to N - 1 loop
                c_row(i) <= SE(LAST - i + 2, LAST);
            end loop;
            -- Buffer c43, c53, ...
            for i in 0 to N - 4 loop
                buf(2, i) <= SE(LAST, LAST - 1 - i);
            end loop;
        elsif next_cnt = LAST + 3 then
            -- Output c41, c42, c43
            for i in 0 to 2 loop
                c_row(i) <= buf(i, 2 - i);
            end loop;
            -- Output c44
            for i in 3 to N - 1 loop
                c_row(i) <= SE(LAST - i + 3, LAST);
            end loop;
            -- Buffer c54, c64, ...
            for i in 0 to N - 5 loop
                buf(3, i) <= SE(LAST, LAST - 1 - i);
            end loop;
        elsif next_cnt = LAST + 4 then
            -- Output buffered elements
            for i in 0 to 3 loop
                c_row(i) <= buf(i, 3 - i);
            end loop;
            -- Output c55
            for i in 4 to N - 1 loop
                c_row(i) <= SE(LAST - i + 4, LAST);
            end loop;
            -- Bufferr c65, c75
            for i in 0 to N - 6 loop
                buf(4, i) <= SE(LAST, LAST - 1 - i);
            end loop;
        else
            -- Default things, to avoid latches being inferred.
            for i in 0 to N - 1 loop
                c_row(i) <= 0;
            end loop;
            for i in 0 to N loop
                for j in 0 to N - 2 loop
                    buf(i, j) <= 0;
                end loop;
            end loop;
        end if;

        if rising_edge(clk) then
            if p then
                --report_systolic;
            end if;
            if rstn = '0' then
                for r in 0 to LAST loop
                    for c in 0 to LAST loop
                        if r < LAST then
                            E(r, c) <= -1;
                        end if;
                        SE(r, c) <= -1;
                        if c < LAST then
                            S(r, c) <= -1;
                        end if;
                    end loop;
                end loop;
            else
                for r in 0 to LAST - 1 loop
                    for c in 0 to LAST - 1 loop
                        SE(r + 1, c + 1) <= SE(r, c) + S(r, c) * E(r, c);
                        E(r, c + 1) <= E(r, c);
                        S(r + 1, c) <= S(r, c);
                    end loop;
                end loop;
            end if;
        end if;
    end process;
end rtl;
