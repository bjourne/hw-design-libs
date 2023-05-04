-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
--
-- A module for computing a histogram of an input array based on dividing the
-- work out onto multiple addition units.
library bjourne;
library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;
use bjourne.all;
use bjourne.types.all;

entity histogram is
    generic (
        N : positive := 8;
        M : positive := 4;
        K : positive := 4
    );
    port (
        clk, nrst : in std_logic;
        A : in integer_vector(0 to N - 1);
        H : out integer_vector(0 to M - 1)
    );
end histogram;

architecture rtl of histogram is
    signal i : natural;
    signal buf : int_array2d_t(0 to K - 1)(0 to M - 1);
begin
    process(clk)
        variable v0, v1, s, v : natural;
    begin
        if rising_edge(clk) then
            if nrst = '0' then
                i <= 0;
                buf <= (others => (others => 0));
            else
                if i = N then
                    report "done";
                    for n in 0 to M - 1 loop
                        s := 0;
                        for j in 0 to K - 1 loop
                            s := s + buf(j)(n);
                        end loop;
                        H(n) <= s;
                    end loop;
                else
                    for j in 0 to K - 1 loop
                        v := A(i + j);
                        buf(j)(v) <= buf(j)(v) + 1;
                    end loop;
                    i <= i + K;
                end if;
            end if;
        end if;
    end process;
end architecture;
