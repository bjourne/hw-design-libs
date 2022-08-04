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

        -- Defaults
        if next_cnt < LAST then
            for i in 0 to N - 1 loop
                c_row(i) <= 0;
            end loop;
            for i in 0 to N loop
                for j in 0 to N - 2 loop
                    buf(i, j) <= 0;
                end loop;
            end loop;
        else
            -- r is row to emit
            for r in 0 to N - 1 loop
                if next_cnt = LAST + r then
                    -- Buffered elements
                    for i in 0 to -1 + r loop
                        c_row(i) <= buf(i, -1 + r - i);
                    end loop;
                    -- Output edges elements
                    for i in r to N - 1 loop
                        c_row(i) <= SE(LAST - i + r, LAST);
                    end loop;
                    -- Buffer a row
                    for i in 0 to N - 2 - r loop
                        buf(r, i) <= SE(LAST, LAST - 1 - i);
                    end loop;
                end if;
            end loop;
        end if;
        if rising_edge(clk) then
            if p then
                report_systolic;
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
