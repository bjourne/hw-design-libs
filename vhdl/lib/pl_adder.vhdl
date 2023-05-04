-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;

entity pl_adder is
    generic (
        LATENCY : positive := 4
    );
    port (
        clk, nrst : in std_logic;

        -- Communication protocol
        in_valid : in std_logic;
        in_ready, out_valid : out std_logic;

        -- Data signals
        x, y : in integer;
        z : out integer
    );
end pl_adder;

architecture rtl of pl_adder is
    signal p, begin_p : std_logic;
    signal i : integer;
begin
    in_ready <= not(p);
    begin_p <= in_valid and in_ready;
    out_valid <= '1' when (p = '1' and i = 0) else '0';
    process(clk)
    begin
        if rising_edge(clk) then
            if nrst = '0' then
                p <= '0';
                i <= 0;
            else
                if begin_p then
                    p <= '1';
                elsif i = 1 then
                    -- We post the result one cycle earlier.
                    z <= x +  y;
                elsif i = 0 then
                    p <= '0';
                else
                    p <= p;
                end if;
                i <= LATENCY - 1 when begin_p else i - 1;
            end if;
        end if;
    end process;
end architecture;
