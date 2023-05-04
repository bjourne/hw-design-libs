-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use bjourne.all;

entity tb_histogram is
end tb_histogram;

architecture beh of tb_histogram is
    signal clk, nrst : std_logic;
    signal A : integer_vector(0 to 7);
    signal H : integer_vector(0 to 7);
begin
    histogram_0: entity histogram
        port map (
            clk => clk,
            nrst => nrst,
            H => H,
            A => A
        );
    process
    begin
        H <= (others => 0);
        A <= (1, 2, 3, 4, 5, 6, 7, 0);
        assert false report "all tests passed" severity note;
        wait;
    end process;
end architecture;
