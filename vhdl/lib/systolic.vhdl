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
        write(file_line, string'("Tick #"));
        write(file_line, cnt);
        write(file_line, string'(" E:"));
        writeline(output, file_line);
        for r in 0 to LAST - 1 loop
            write(file_line, r, right, 3);
            for c in 0 to LAST loop
                write(file_line, E(r, c), right, 4);
            end loop;
            writeline(output, file_line);
        end loop;
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
                for i in 0 to -1 loop
                    E(i, 0) <= 0;
                    S(0, i) <= 0;
                end loop;
                for i in 0 to N - 1 loop
                    E(i, 0) <= a_row(i - 0);
                    S(0, i) <= b_col(i - 0);
                end loop;
                for i in N to LAST - 1 loop
                    E(i, 0) <= 0;
                    S(0, i) <= 0;
                end loop;
            when 1 =>
                for i in 0 to 0 loop
                    E(i, 0) <= 0;
                    S(0, i) <= 0;
                end loop;
                for i in 1 to N loop
                    E(i, 0) <= a_row(i - 1);
                    S(0, i) <= b_col(i - 1);
                end loop;
                for i in N + 1 to LAST - 1 loop
                    E(i, 0) <= 0;
                    S(0, i) <= 0;
                end loop;
            when 2 =>
                for i in 0 to 1 loop
                    E(i, 0) <= 0;
                    S(0, i) <= 0;
                end loop;
                for i in 2 to N + 1 loop
                    E(i, 0) <= a_row(i - 2);
                    S(0, i) <= b_col(i - 2);
                end loop;
                for i in N + 2 to LAST - 1 loop
                    E(i, 0) <= 0;
                    S(0, i) <= 0;
                end loop;
            when 5 =>
                c_row(0) <= SE(LAST - 0, LAST);
                c_row(1) <= SE(LAST - 1, LAST);
                c_row(2) <= SE(LAST - 2, LAST);
                buf(0) <=   SE(LAST, LAST - 1);
                buf(1) <=   SE(LAST, LAST - 2);
            when 6 =>
                c_row(0) <= buf(0);
                c_row(1) <= SE(LAST - 0, LAST);
                c_row(2) <= SE(LAST - 1, LAST);
                buf(0) <=   SE(LAST, LAST - 1);
            when 7 =>
                c_row(0) <= buf(1);
                c_row(1) <= buf(0);
                c_row(2) <= SE(LAST, LAST);
            when others =>
                for i in 0 to N + 1 loop
                    E(i, 0) <= -1;
                    S(0, i) <= -1;
                end loop;
                for i in 0 to N - 1 loop
                    c_row(i) <= 0;
                end loop;
                buf(0) <= -1;
                buf(1) <= -1;
        end case;
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
