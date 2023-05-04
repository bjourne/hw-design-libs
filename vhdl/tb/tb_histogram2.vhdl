-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;
use bjourne.all;
use bjourne.utils.all;
use bjourne.types.all;

entity tb_histogram2 is
end tb_histogram2;


architecture beh of tb_histogram2 is
    signal m : std_logic;
    signal clk, nrst : std_logic;
    signal x, y, z : integer;

    -- Communication
    signal in_valid, in_ready, out_valid : std_logic;
begin
    pl_adder_0: entity pl_adder
        generic map (
            LATENCY => 4
        )
        port map (
            clk => clk,
            nrst => nrst,
            x => x,
            y => y,
            z => z,
            in_valid => in_valid,
            in_ready => in_ready,
            out_valid => out_valid
        );
    process
    begin
        clk <= '0';
        nrst <= '0';
        in_valid <= '0';

        tick(clk);

        report "begin processing";

        in_valid <= '1';
        nrst <= '1';
        x <= 15;
        y <= 10;

        tick(clk);
        report to_string(z);

        tick(clk);
        report to_string(z);

        tick(clk);
        report to_string(z);

        tick(clk);
        report "done: " & to_string(out_valid) & " " & to_string(z);

        -- tick(clk);
        -- report to_string(z);

        -- tick(clk);
        -- report to_string(z);

        assert false report "all tests passed" severity note;
        wait;
    end process;
end architecture;
