-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use bjourne.all;
use bjourne.types.all;
use bjourne.utils.all;

entity tb_dct8x8 is
end tb_dct8x8;

architecture beh of tb_dct8x8 is
    signal clk, rstn : std_logic;
    signal x : real_array2d_t(0 to 7)(0 to 7);
    signal y : real_array2d_t(0 to 7)(0 to 7);
begin
    dct8x8_0: entity dct8x8
        port map (
            clk => clk,
            rstn => rstn,
            x => x,
            y => y
        );
    process
        variable line0 : line;
    begin
        clk <= '0';
        rstn <= '0';
        tick(clk);
        rstn <= '1';

        x <= (
            (83.0, 86.0, 77.0, 15.0, 93.0, 35.0, 86.0, 92.0),
            (49.0, 21.0, 62.0, 27.0, 90.0, 59.0, 63.0, 26.0),
            (40.0, 26.0, 72.0, 36.0, 11.0, 68.0, 67.0, 29.0),
            (82.0, 30.0, 62.0, 23.0, 67.0, 35.0, 29.0,  2.0),
            (22.0, 58.0, 69.0, 67.0, 93.0, 56.0, 11.0, 42.0),
            (29.0, 73.0, 21.0, 19.0, 84.0, 37.0, 98.0, 24.0),
            (15.0, 70.0, 13.0, 26.0, 91.0, 80.0, 56.0, 73.0),
            (62.0, 70.0, 96.0, 81.0,  5.0, 25.0, 84.0, 27.0)
        );
        tick(clk);
        x <= (
            (144.0, 139.0, 149.0, 155.0, 153.0, 155.0, 155.0, 155.0),
            (151.0, 151.0, 151.0, 159.0, 156.0, 156.0, 156.0, 158.0),
            (151.0, 156.0, 160.0, 162.0, 159.0, 151.0, 151.0, 151.0),
            (158.0, 163.0, 161.0, 160.0, 160.0, 160.0, 160.0, 161.0),
            (158.0, 160.0, 161.0, 162.0, 160.0, 155.0, 155.0, 156.0),
            (161.0, 161.0, 161.0, 161.0, 160.0, 157.0, 157.0, 157.0),
            (162.0, 162.0, 161.0, 160.0, 161.0, 157.0, 157.0, 157.0),
            (162.0, 162.0, 161.0, 160.0, 163.0, 157.0, 158.0, 154.0)
        );
        tick(clk);
        x <= (others => (others => 33.0));
        for i in 1 to 20 loop
            write(line0, string'("*** y ***"));
            writeline(output, line0);
            io.write_arr(y);
            tick(clk);
        end loop;



        assert false report "all tests passed" severity note;
        wait;
    end process;
end architecture;
