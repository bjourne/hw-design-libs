-- Copyright (C) 2022-2023 Björn A. Lindqvist <bjourne@gmail.com>
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.float_pkg.all;

package math is
    pure function log2ceil(a : positive) return natural;
    pure function inv_sqrt(a : float32) return float32;
end package math;
package body math is
    pure function log2ceil(a : positive) return natural is
        variable i, cnt : natural;
    begin
        i := a - 1;
        cnt := 0;
        while i > 0 loop
            cnt := cnt + 1;
            i := to_integer(shift_right(to_unsigned(i, 32), 1));
        end loop;
        return cnt;
    end function;
    pure function inv_sqrt(a : float32) return float32 is
        variable i : unsigned(31 downto 0);
        variable x, ah, c : float32;
    begin
        ah := to_float(0.5) * a;
        c := to_float(1.5);
        i := 1597463174 - shift_right(unsigned(to_slv(a)), 1);
        x := float32(std_logic_vector(i));
        return x * (c - ah * x * x);
    end function;
end math;
