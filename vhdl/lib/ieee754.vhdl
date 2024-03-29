-- Copyright (C) 2022-2023 Björn A. Lindqvist <bjourne@gmail.com>
--
-- VHDL 2008 supports ieee754 floating point types, but I  think it is fun to
-- write the code manually.
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library work;

package ieee754 is
    -- NaN and +/-Inf are not handled.
    pure function float32_to_int32(f : std_logic_vector(31 downto 0))
        return signed;
    pure function int32_to_float32(i : signed(31 downto 0))
        return std_ulogic_vector;
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
            return to_signed(0, 32);
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
    pure function int32_to_float32(i : signed(31 downto 0))
        return std_ulogic_vector is
        variable result : std_ulogic_vector(31 downto 0);
    begin
        if i = 0 then
            result := X"00000000";
        else
            result := X"42c80000";
        end if;
        return result;
    end function;
end ieee754;
