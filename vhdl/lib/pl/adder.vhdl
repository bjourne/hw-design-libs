-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
-- Need to figure out how subpackages work.
library bjourne_pl;
library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;

entity adder is
    generic (
        LATENCY : positive := 4
    );
    port (
        clk, nrst : in std_logic;

        -- Upstream ports
        u0_v : in std_logic;
        u0_r : out std_logic;
        u0_d : in integer;

        u1_v : in std_logic;
        u1_r : out std_logic;
        u1_d : in integer;

        -- Downstream ports
        d0_v : out std_logic;
        d0_r : in std_logic;
        d0_d : out integer
    );
end adder;

architecture rtl of adder is
    signal o0, o1 : integer;
    signal i : integer;
begin
    process(clk)
    begin
        if rising_edge(clk) then
            if nrst = '0' then
                u0_r <= '1';
                u1_r <= '1';
                d0_v <= '0';
                i <= 0;
            else
                if u0_v and u0_r then
                    u0_r <= '0';
                    o0 <= u0_d;
                end if;
                if u1_v and u1_r then
                    u1_r <= '0';
                    o1 <= u1_d;
                end if;

                if (u0_r = '0') and (u1_r = '0') and (i = 0) then
                    i <= LATENCY;
                    d0_v <= '0';
                elsif i > 0 then
                    i <= i - 1;
                else
                    i <= 0;
                end if;
                if i = 1 then
                    d0_d <= o0 + o1;
                    d0_v <= '1';

                    u0_r <= '1';
                    u1_r <= '1';
                end if;
            end if;
        end if;
    end process;
end architecture;
