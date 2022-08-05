-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
--
-- This systolic array multiplier is awesome.
library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;
use std.textio.all;

entity systolic2 is
    generic(
        N : integer
    );
    port(
        clk : in std_logic;
        rstn : in std_logic;
        start : in std_logic;
        a_row : in integer_vector(0 to N - 1);
        b_col : in integer_vector(0 to N - 1);
        c_row : out integer_vector(0 to N - 1)
    );
end entity;

architecture rtl of systolic2 is

    constant HEIGHT : integer := 3*N - 2;
    constant WIDTH : integer := 2*N - 1;

    type east_t is array(0 to HEIGHT - 1, 0 to WIDTH) of integer;
    type south_t is array(0 to HEIGHT, 0 to WIDTH - 1) of integer;
    type south_east_t is array(0 to HEIGHT, 0 to WIDTH) of integer;

    signal cnt : natural;
    signal p : std_logic;

    signal E : east_t;
    signal S : south_t;
    signal SE : south_east_t;

    procedure debug_systolic is
        variable fstatus : file_open_status;
        variable file_line : line;
        file fptr : text;
    begin
        write(file_line, string'("Tick #"));
        write(file_line, cnt);
        write(file_line, string'(" SE:"));
        writeline(output, file_line);
        for r in 0 to HEIGHT loop
            write(file_line, r, right, 3);
            for c in 0 to WIDTH loop
                write(file_line, SE(r, c), right, 5);
            end loop;
            writeline(output, file_line);
        end loop;
    end;
    procedure reset_array(signal cnt0 : out natural;
                          signal E0 : out east_t;
                          signal S0 : out south_t;
                          signal SE0 : out south_east_t) is
    begin
        for r in 0 to HEIGHT loop
            for c in 0 to WIDTH loop
                SE0(r, c) <= 0;
                if (r < HEIGHT) then
                    E0(r, c) <= 0;
                end if;
                if (c < WIDTH) then
                    S0(r, c) <= 0;
                end if;
            end loop;
        end loop;
        cnt0 <= 0;
    end;
    procedure read_input(cycle : integer;
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
        for i in cycle + N to HEIGHT - 1 loop
            E0(i, 0) <= 0;
        end loop;
        for i in cycle + N to WIDTH - 1 loop
            S0(0, i) <= 0;
        end loop;
    end;
    procedure write_output(cycle : integer;
                           signal res : out integer_vector(0 to N - 1);
                           signal SE0 : in south_east_t) is
    begin
        for i in 0 to N - 1 loop
            res(i) <= SE0(cycle + WIDTH - i, WIDTH);
        end loop;
    end;
begin
    process (clk, cnt, start)
        variable next_cnt : natural;
    begin
        if start then
            next_cnt := 0;
        else
            next_cnt := cnt + 1;
        end if;

        -- Input to the array.
        for i in 0 to WIDTH loop
            SE(0, i) <= 0;
        end loop;
        for i in 0 to HEIGHT loop
            SE(i, 0) <= 0;
        end loop;
        read_input(next_cnt rem N, a_row, b_col, E, S);
        write_output((next_cnt + 1) rem N, c_row, SE);

        if rising_edge(clk) then
            debug_systolic;
            cnt <= next_cnt;
            if rstn = '0' then
                reset_array(cnt, E, S, SE);
            else
                for r in 0 to HEIGHT - 1 loop
                    for c in 0 to WIDTH - 1 loop
                        SE(r + 1, c + 1) <= SE(r, c) + S(r, c) * E(r, c);
                        S(r + 1, c) <= S(r, c);
                        E(r, c + 1) <= E(r, c);
                    end loop;
                end loop;
            end if;
        end if;
    end process;
end rtl;
