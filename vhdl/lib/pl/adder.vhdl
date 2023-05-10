-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
-- Need to figure out how subpackages work.
library bjourne;
library bjourne_pl;
library ieee;
use bjourne.utils.all;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;

entity adder is
    generic(
        SEED : integer
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
        variable lat : integer;
        variable seed1 : integer := SEED;
        variable seed2 : integer := SEED + 10;
    begin
        if rising_edge(clk) then
            if nrst = '0' then
                u0_r <= '1';
                u1_r <= '1';
                d0_v <= '0';
                i <= 0;
            else
                -- Idle state
                if i = 0 then
                    -- Transfer inputs
                    if u0_v and u0_r then
                        u0_r <= '0';
                        o0 <= u0_d;
                    end if;
                    if u1_v and u1_r then
                        u1_r <= '0';
                        o1 <= u1_d;
                    end if;
                    -- Begin computation
                    if (u0_r = '0') and (u1_r = '0')  then
                        rand_range(seed1, seed2, 10, lat);
                        i <= 2 + lat;
                        -- Invalidate output while we're computing.
                        d0_v <= '0';
                    end if;
                else
                    -- Transer outputs
                    if i = 1 then
                        if d0_r then
                            d0_d <= o0 + o1;
                            d0_v <= '1';
                            u0_r <= '1';
                            u1_r <= '1';
                            i <= i - 1;
                        else
                            report "stall!";
                            i <= i;
                        end if;
                    else
                        i <= i - 1;
                    end if;
                end if;
            end if;
        end if;
    end process;
end architecture;
