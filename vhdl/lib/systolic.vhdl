-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
--
-- For an explanation on how this works, see
-- https://www.youtube.com/watch?v=vADVh1ogNo0
--
-- Sustained throughput is 1 matrix per N cycles.
library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;
use std.textio.all;

entity systolic is
    generic(
        N : integer; DEBUG : boolean
    );
    port(
        clk, rstn : in std_logic;
        start : in std_logic;
        a_row, b_col : in integer_vector(0 to N - 1);
        c_row : out integer_vector(0 to N - 1)
    );
end entity;
architecture rtl of systolic is
    constant HEIGHT : integer := 3*N - 2;
    constant WIDTH : integer := 2*N - 1;

    type east_t is array(0 to HEIGHT - 1, 0 to WIDTH) of integer;
    type south_t is array(0 to HEIGHT, 0 to WIDTH - 1) of integer;
    type south_east_t is array(0 to HEIGHT, 0 to WIDTH) of integer;

    signal cnt : natural;
    signal E : east_t;
    signal S : south_t;
    signal SE : south_east_t;

    procedure debug_systolic is
        variable file_line : line;
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
begin
    process (clk, cnt, start)
        variable next_cnt, r_cycle, w_cycle : natural;
    begin
        next_cnt := 0 when start else cnt + 1;
        for i in 0 to WIDTH loop
            SE(0, i) <= 0;
        end loop;
        for i in 0 to HEIGHT loop
            SE(i, 0) <= 0;
        end loop;

        -- Write to north and west.
        r_cycle := 0 when next_cnt = N else next_cnt;
        for i in 0 to r_cycle - 1 loop
            E(i, 0) <= 0;
            S(0, i) <= 0;
        end loop;
        for i in r_cycle to r_cycle + N - 1 loop
            E(i, 0) <= a_row(i - r_cycle);
            S(0, i) <= b_col(i - r_cycle);
        end loop;
        for i in r_cycle + N to HEIGHT - 1 loop
            E(i, 0) <= 0;
        end loop;
        for i in r_cycle + N to WIDTH - 1 loop
            S(0, i) <= 0;
        end loop;

        -- Read from east.
        w_cycle := 0 when r_cycle + 1 = N else r_cycle + 1;
        for i in 0 to N - 1 loop
            c_row(i) <= SE(w_cycle + WIDTH - i, WIDTH);
        end loop;
        if rising_edge(clk) then
            if DEBUG then
                debug_systolic;
            end if;
            if rstn = '0' then
                cnt <= 0;
                SE <= (others => (others => 0));
                E <= (others => (others => 0));
                S <= (others => (others => 0));
            else
                for r in 0 to HEIGHT - 1 loop
                    for c in 0 to WIDTH - 1 loop
                        SE(r + 1, c + 1) <= SE(r, c) + S(r, c) * E(r, c);
                        S(r + 1, c) <= S(r, c);
                        E(r, c + 1) <= E(r, c);
                    end loop;
                end loop;
                cnt <= 0 when next_cnt = N else next_cnt;
            end if;
        end if;
    end process;
end rtl;
