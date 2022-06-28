-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
use bjourne.all;
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity tb_math is
end tb_math;

architecture beh of tb_math is
begin
    process
    begin
        assert math.log2ceil(4) = 2;
        assert math.log2ceil(9) = 4;
        assert false report "all tests passed" severity note;
        wait;
    end process;
end beh;
