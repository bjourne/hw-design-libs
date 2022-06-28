-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package math is
    pure function log2ceil(a : positive) return natural;
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
end math;
