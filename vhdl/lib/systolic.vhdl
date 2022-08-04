-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;

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

    procedure report_systolic is
    begin
        report "*** Tick #" & to_string(cnt) & " "
            & to_string(in_valid) & " ***";
        report "E:";
        for r in 0 to N + 1 loop
            report to_string(r) & ": "
                & to_string(E(r, 0)) & " "
                & to_string(E(r, 1)) & " "
                & to_string(E(r, 2)) & " "
                & to_string(E(r, 3)) & " "
                & to_string(E(r, 4)) & " "
                & to_string(E(r, 5));
        end loop;
        report "SE:";
        for r in 0 to N + 2 loop
            report to_string(r) & ": "
                & to_string(SE(r, 0)) & " "
                & to_string(SE(r, 1)) & " "
                & to_string(SE(r, 2)) & " "
                & to_string(SE(r, 3)) & " "
                & to_string(SE(r, 4)) & " "
                & to_string(SE(r, 5));
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
                E(0, 0) <= a_row(0);
                E(1, 0) <= a_row(1);
                E(2, 0) <= a_row(2);
                E(3, 0) <= 0;
                E(4, 0) <= 0;

                S(0, 0) <= b_col(0);
                S(0, 1) <= b_col(1);
                S(0, 2) <= b_col(2);
                S(0, 3) <= 0;
                S(0, 4) <= 0;
            when 1 =>
                E(0, 0) <= 0;
                E(1, 0) <= a_row(0);
                E(2, 0) <= a_row(1);
                E(3, 0) <= a_row(2);
                E(4, 0) <= 0;

                S(0, 0) <= 0;
                S(0, 1) <= b_col(0);
                S(0, 2) <= b_col(1);
                S(0, 3) <= b_col(2);
                S(0, 4) <= 0;
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
            when 4 =>
                c_out(0) <= SE(3, 4);
                c_out(1) <= SE(4, 4);
                c_out(2) <= SE(4, 3);
            when 5 =>
                c_out(0) <= SE(3, 5);
                c_out(1) <= SE(4, 4);
                c_out(2) <= SE(5, 3);
            when 6 =>
                c_out(0) <= SE(4, 5);
                c_out(1) <= SE(5, 5);
                c_out(2) <= SE(5, 4);
            when 7 =>
                c_out(0) <= SE(5, 5);
                c_out(1) <= SE(5, 5);
                c_out(2) <= SE(5, 5);
            when others =>
                for i in 0 to N + 1 loop
                    E(i, 0) <= 0;
                    S(0, i) <= 0;
                end loop;
                for i in 0 to N - 1 loop
                    c_out(i) <= 0;
                end loop;
        end case;
        if rising_edge(clk) then
            for r in 0 to 4 loop
                for c in 0 to 4 loop
                    SE(r + 1, c + 1) <= SE(r, c) + S(r, c) * E(r, c);
                    E(r, c + 1) <= E(r, c);
                    S(r + 1, c) <= S(r, c);
                end loop;
            end loop;
        end if;
    end process;
end rtl;
