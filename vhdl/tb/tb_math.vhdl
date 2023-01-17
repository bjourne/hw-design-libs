-- Copyright (C) 2022-2023 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
use bjourne.all;
library ieee;
use ieee.float_pkg.all;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;

entity tb_math is
end tb_math;

architecture beh of tb_math is
    signal f : float32;
begin
    process
    begin
        assert math.log2ceil(4) = 2;
        assert math.log2ceil(9) = 4;

        assert abs(to_real(math.inv_sqrt(to_float(54.0))) - 0.136) < 0.01;
        assert abs(to_real(math.inv_sqrt(to_float(256.0))) - 0.063) < 0.01;
        assert abs(to_real(math.inv_sqrt(to_float(1500.0))) - 0.026) < 0.01;

        assert false report "all tests passed" severity note;
        wait;
    end process;
end beh;
