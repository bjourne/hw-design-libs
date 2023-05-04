-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
--
-- A module for computing a histogram of an input array. The point of this is
-- to demonstrate loops that are hard to schedule efficiently.

library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;

entity histogram is
    port (
        clk, nrst : in std_logic;
        A : in integer_vector(0 to 7);
        H : out integer_vector(0 to 7)
    );
end histogram;

architecture rtl of histogram is
    signal i : natural;
begin
    process(clk)
    begin
        if rising_edge(clk) then
            if nrst = '0' then
                i <= 0;
            else
            end if;
        end if;
    end process;
end architecture;
