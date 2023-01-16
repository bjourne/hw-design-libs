-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use bjourne.all;
use bjourne.utils.all;

entity tb_dct8 is
end tb_dct8;

architecture beh of tb_dct8 is
    signal clk, rstn : std_logic;
    signal x : real_vector(0 to 7);
    signal y : real_vector(0 to 7);
    signal r : real;
begin
    dct8_0: entity dct8
        port map (
            clk => clk,
            rstn => rstn,
            x => x,
            y => y
        );
    process
        variable line0 : line;
    begin
        x <= (others => 0.0);
        clk <= '0';
        rstn <= '0';
        tick(clk);
        rstn <= '1';
        tick(clk);


        x <= (20.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0);

        tick(clk);
        io.write_arr(y);

        x <= (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0);

        tick(clk);
        io.write_arr(y);

        tick(clk);
        io.write_arr(y);

        tick(clk);
        io.write_arr(y);

        tick(clk);
        io.write_arr(y);

        tick(clk);
        io.write_arr(y);

        tick(clk);
        io.write_arr(y);

        tick(clk);
        io.write_arr(y);

        tick(clk);
        io.write_arr(y);

        tick(clk);
        io.write_arr(y);

        tick(clk);
        io.write_arr(y);


        assert false report "all tests passed" severity note;
        wait;
    end process;
end architecture;
