-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use ieee.math_real.all;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;

package utils is
    procedure tick(signal c : inout std_logic);
    procedure rand_range(seed1, seed2 : inout positive;
                         max : natural;
                         value : out integer);
end package;
package body utils is
    procedure rand_range(seed1, seed2 : inout positive;
                         max : natural;
                         value : out integer) is
        variable r : real;
    begin
        uniform(seed1, seed2, r);
        value := integer(round(r * real(max)));
    end;
    procedure tick(signal c : inout std_logic) is
    begin
        wait for 10 ns;
        c <= not c;
        wait for 10 ns;
        c <= not c;
    end;
end;
