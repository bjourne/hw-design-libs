-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library work;

package ieee754 is
    -- NaN and +/-Inf are not handled.
    pure function float32_to_int32(f : std_logic_vector(31 downto 0))
        return signed;
end package ieee754;
package body ieee754 is
    pure function float32_to_int32(f : std_logic_vector(31 downto 0))
        return signed is
        variable s_bexp : signed(7 downto 0);
        variable s_frac : signed(31 downto 0) := X"00000000";
    begin
        s_bexp := signed(f(30 downto 23));
        -- Zero check.
        if s_bexp = 0 then
            return to_signed(0, 24);
        end if;
        s_bexp := s_bexp - 127;
        s_frac(22 downto 0) := signed(f(22 downto 0));
        s_frac(23) := '1';
        if s_bexp < 23 then
            s_frac := shift_right(s_frac, to_integer(23 - s_bexp));
        elsif s_bexp > 23 then
            s_frac := shift_left(s_frac, to_integer(s_bexp - 23));
        end if;
        if f(31) = '1' then
            return -s_frac;
        else
            return s_frac;
        end if;
    end function;
end ieee754;
