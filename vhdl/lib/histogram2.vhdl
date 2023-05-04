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

entity histogram2 is
    generic (
        N : positive := 8;
        M : positive := 4
    );
    port (
        clk, nrst : in std_logic
    );
end histogram2;

architecture rtl of histogram2 is
begin

end architecture;
