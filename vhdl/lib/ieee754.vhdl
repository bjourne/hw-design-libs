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
        variable bexp : signed(7 downto 0);
        variable frac : signed(31 downto 0);
    begin
        bexp := signed(f(30 downto 23));
        -- Zero check.
        if bexp = 0 then
            return to_signed(0, 24);
        end if;
        bexp := bexp - 127;
        frac := "000000001" & signed(f(22 downto 0));
        if bexp < 23 then
            frac := shift_right(frac, to_integer(23 - bexp));
        elsif bexp > 23 then
            frac := shift_left(frac, to_integer(bexp - 23));
        end if;
        if f(31) = '1' then
            return -frac;
        else
            return frac;
        end if;
    end function;
end ieee754;
