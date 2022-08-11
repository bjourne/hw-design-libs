-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
--
-- A simple dual port block RAM abstraction.
-- Inspired by: https://github.com/VLSI-EDA/PoC/blob/master/src/mem/ocram/ocram_tdp_sim.vhdl
library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;

entity dp_bram is
    generic (
        DEPTH : positive := 1000
    );
    port (
        clk_a, clk_b : in std_logic;
        we_a, we_b : in std_logic;
        addr_a, addr_b : in natural;
        din_a, din_b : in integer;
        dout_a, dout_b : out integer
    );
end dp_bram;
architecture rtl of dp_bram is
    type ram_t is array (0 to DEPTH - 1) of integer;
    signal ram : ram_t;
begin
    process (clk_a, clk_b)
        variable write_a, write_b : boolean;
    begin
        write_a := false;
        write_b := false;
        if rising_edge(clk_a) then
            if  (we_a) then
                write_a := true;
                ram(addr_a) <= din_a;
                dout_a <= din_a;
            else
                dout_a <= ram(addr_a);
            end if;
        end if;
        if rising_edge(clk_b) then
            if  (we_b) then
                write_b  := true;
                ram(addr_b) <= din_b;
                dout_b <= din_b;
            else
                dout_b <= ram(addr_b);
            end if;
        end if;
        if addr_a = addr_b then
            if write_a then
                if write_b then
                    dout_a <= din_b;
                else
                    dout_b <= din_a;
                end if;
            elsif write_b then
                dout_a <= din_b;
            end if;
        end if;
    end process;
end rtl;
