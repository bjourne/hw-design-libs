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
        c_out : out integer_vector(0 to N - 1)
    );
end entity;

architecture rtl of systolic is
    type east_t is array(0 to N + 1, 0 to N + 2) of integer;
    type south_t is array(0 to N + 2, 0 to N + 1) of integer;
    type south_east_t is array(0 to N + 2, 0 to N + 2) of integer;

    signal cnt : natural;
    signal p : std_logic;

    signal E : east_t;
    signal S : south_t;
    signal SE : south_east_t;

    -- Random buffer
    signal buf : integer_vector(0 to 1);

    procedure report_systolic is
        variable fstatus : file_open_status;
        variable file_line : line;
        file fptr : text;
    begin
        -- write(file_line, string'("Tick #"));
        -- write(file_line, cnt);
        -- write(file_line, string'(" E:"));
        -- writeline(output, file_line);
        -- for r in 0 to N + 1 loop
        --     write(file_line, r, right, 3);
        --     for c in 0 to N + 2 loop
        --         write(file_line, E(r, c), right, 4);
        --     end loop;
        --     writeline(output, file_line);
        -- end loop;
        write(file_line, string'("Tick #"));
        write(file_line, cnt);
        write(file_line, string'(" SE:"));
        writeline(output, file_line);
        for r in 0 to N + 2 loop
            write(file_line, r, right, 3);
            for c in 0 to N + 2 loop
                write(file_line, SE(r, c), right, 4);
            end loop;
            writeline(output, file_line);
        end loop;
    end;
begin
    process (clk, cnt, in_valid)
        variable next_cnt : natural;
    begin
        -- Process control
        in_ready <= not p;
        if in_ready and in_valid then
            next_cnt := 0;
        else
            next_cnt := cnt + 1;
        end if;
        if rising_edge(clk) then
            if rstn = '0' then
                p <= '0';
            elsif in_ready and in_valid then
                p <= '1';
            elsif next_cnt = 6 then
                p <= '0';
            end if;
            cnt <= next_cnt;
        end if;

        -- Systolic array handling
        for i in 0 to N + 1 loop
            SE(0, i) <= 0;
            SE(i, 0) <= 0;
        end loop;
        case next_cnt is
            when 0 =>
                for i in 0 to N - 1 loop
                    E(i, 0) <= a_row(i);
                    S(0, i) <= b_col(i);
                end loop;
                for i in N to N + 1 loop
                    E(i, 0) <= 0;
                    S(0, i) <= 0;
                end loop;
            when 1 =>
                for i in 0 to N - 1 loop
                    E(1 + i, 0) <= a_row(i);
                    S(0, 1 + i) <= b_col(i);
                end loop;
                E(0, 0) <= 0;
                E(N + 1, 0) <= 0;
                S(0, 0) <= 0;
                S(0, N + 1) <= 0;
            when 2 =>
                E(0, 0) <= 0;
                E(1, 0) <= 0;
                E(2, 0) <= a_row(0);
                E(3, 0) <= a_row(1);
                E(4, 0) <= a_row(2);

                S(0, 0) <= 0;
                S(0, 1) <= 0;
                S(0, 2) <= b_col(0);
                S(0, 3) <= b_col(1);
                S(0, 4) <= b_col(2);
            when 5 =>
                c_out(0) <= SE(5, 5);
                c_out(1) <= SE(4, 5);
                c_out(2) <= SE(3, 5);

                buf(0) <= SE(5, 4);
                buf(1) <= SE(5, 3);
            when 6 =>
                c_out(0) <= buf(0);
                c_out(1) <= SE(5, 5);
                c_out(2) <= SE(4, 5);

                buf(0) <= SE(5, 4);
            when 7 =>
                c_out(0) <= buf(1);
                c_out(1) <= buf(0);
                c_out(2) <= SE(5, 5);
            when others =>
                for i in 0 to N + 1 loop
                    E(i, 0) <= -1;
                    S(0, i) <= -1;
                end loop;
                for i in 0 to N - 1 loop
                    c_out(i) <= 0;
                end loop;
                buf(0) <= -1;
                buf(1) <= -1;
        end case;
        if rising_edge(clk) then
            report_systolic;
            if rstn = '0' then
                for r in 0 to N + 2 loop
                    for c in 0 to N + 2 loop
                        if r < N + 2 then
                            E(r, c) <= -1;
                        end if;
                        SE(r, c) <= -1;
                        if c < N + 2 then
                            S(r, c) <= -1;
                        end if;
                    end loop;
                end loop;
            else
                for r in 0 to N + 1 loop
                    for c in 0 to N + 1 loop
                        SE(r + 1, c + 1) <= SE(r, c) + S(r, c) * E(r, c);
                        E(r, c + 1) <= E(r, c);
                        S(r + 1, c) <= S(r, c);
                    end loop;
                end loop;
            end if;
        end if;
    end process;
end rtl;
