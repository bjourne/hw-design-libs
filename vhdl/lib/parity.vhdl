-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
--
-- Same interface as the IC74180
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- par is the bit that should be added to d to make the sum of the 1s
-- odd or even.
entity parity is

    port(
        d : in std_logic_vector(7 downto 0);
        odd_even : in std_logic;
        par : out std_logic
    );
end entity;

architecture rtl of parity is
begin
    -- parry <= (((d(0) xnor d(1)) xor (d(2) xnor d(3))) xnor
    --           ((d(4) xnor d(5)) xor (d(6) xnor d(7))));
    -- not_parry <= not parry;

    -- sum_even <= (parry nand odd) and (not_parry nand even);
    -- sum_odd <= (parry nand even) and (not_parry nand odd);
    par <= xor (d & odd_even);

    -- sum_even <= (xor (d & even));
    -- sum_odd <= not sum_even;
end architecture;
