-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
-- A = [[15, 2, 3],
--      [4, 5, 6],
--      [7, 8, 9]]
-- B = [[10, 11, 12],
--      [13, 14, 15],
--      [16, 17, 18]]

library bjourne;
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use bjourne.all;

entity tb_systolic is
end tb_systolic;

architecture beh of tb_systolic is
    procedure tick(signal c : inout std_logic) is
    begin
        wait for 10 ns;
        c <= not c;
        wait for 10 ns;
        c <= not c;
    end;
    signal clk : std_logic;
    signal rstn : std_logic;
    signal in_valid, in_ready : std_logic;
    signal a_row, b_col, c_out : integer_vector(0 to 2);
begin
    systolic0: entity systolic
        port map (
            clk => clk,
            rstn => rstn,
            in_valid => in_valid,
            in_ready => in_ready,
            a_row => a_row,
            b_col => b_col,
            c_out => c_out
        );
    process
    begin
        clk <= '0';
        rstn <= '0';
        wait for 10 ns;
        tick(clk);

        rstn <= '1';
        tick(clk);


        assert in_ready = '1';
        in_valid <= '1';
        -- Tick 0
        a_row <= (15, 2, 3);
        b_col <= (10, 13, 16);
        tick(clk);

        -- Tick 1
        in_valid <= '0';
        a_row <= (4, 5, 6);
        b_col <= (11, 14, 17);
        tick(clk);

        -- Tick 2
        a_row <= (7, 8, 9);
        b_col <= (12, 15, 18);
        tick(clk);

        -- Tick 3
        a_row <= (0, 0, 0);
        b_col <= (0, 0, 0);

        tick(clk);
        assert c_out = (244, 224, 201);

        tick(clk);
        assert c_out = (264, 216, 318);

        tick(clk);
        assert c_out = (231, 216, 342);

        tick(clk);
        assert c_out = (366, 366, 366);
        assert in_ready = '1';


        assert false report "all tests passed" severity note;
        wait;
    end process;
end architecture;
