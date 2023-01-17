-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use bjourne.all;
use bjourne.utils.all;
use ieee.float_pkg.all;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;
use std.textio.all;


entity tb_invsqrt_f32 is
end tb_invsqrt_f32;

architecture beh of tb_invsqrt_f32 is
    signal clk, rstn : std_logic;
    signal x : float32;
    signal y : float32;
begin
    invsqrt_f32_0: entity invsqrt_f32
        port map (
            clk => clk,
            rstn => rstn,
            x => x,
            y => y
        );
    process begin
        x <= to_float(0.0);

        clk <= '0';
        rstn <= '0';
        tick(clk);
        rstn <= '1';
        tick(clk);
        x <= to_float(54.0);
        tick(clk);
        x <= to_float(256.0);
        tick(clk);
        x <= to_float(1500.0);
        tick(clk);
        tick(clk);
        tick(clk);
        assert abs(to_real(y) - 0.136) < 0.01;
        tick(clk);
        assert abs(to_real(y) - 0.063) < 0.01;
        tick(clk);
        assert abs(to_real(y) - 0.026) < 0.01;

        assert false report "all tests passed" severity note;
        wait;
    end process;
end architecture;
