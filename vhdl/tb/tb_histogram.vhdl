-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use bjourne.all;
use bjourne.utils.all;

entity tb_histogram is
    generic (
        N : positive := 16
    );
end tb_histogram;

architecture beh of tb_histogram is
    signal clk, nrst : std_logic;
    signal A : integer_vector(0 to N - 1);
    signal H : integer_vector(0 to 3);
begin
    histogram_0: entity histogram
        generic map (
            N => N
        )
        port map (
            clk => clk,
            nrst => nrst,
            H => H,
            A => A
        );
    process
    begin
        clk <= '0';
        nrst <= '0';
        tick(clk);

        nrst <= '1';
        A <= (
            1, 1, 1, 2, 3, 2, 1, 0,
            1, 1, 1, 2, 3, 2, 1, 0
        );

        for i in 1 to N + 1 loop
            tick(clk);
            io.write_arr(H);
        end loop;

        assert false report "all tests passed" severity note;
        wait;
    end process;
end architecture;
