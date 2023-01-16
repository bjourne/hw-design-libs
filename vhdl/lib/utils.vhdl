-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

package utils is
    procedure tick(signal c : inout std_logic);
end package;
package body utils is
    procedure tick(signal c : inout std_logic) is
    begin
        wait for 10 ns;
        c <= not c;
        wait for 10 ns;
        c <= not c;
    end;
end;
