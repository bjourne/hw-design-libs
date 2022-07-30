-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
--
-- Same interface as the IC74180
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity parity is
    port(
        d : in std_logic_vector(7 downto 0);
        even : in std_logic;
        odd : in std_logic;
        sum_even : out std_logic;
        sum_odd : out std_logic
    );
end entity;

architecture rtl of parity is
    signal not_parry, parry : std_logic;

begin
    -- parry <= (((d(0) xnor d(1)) xor (d(2) xnor d(3))) xnor
    --           ((d(4) xnor d(5)) xor (d(6) xnor d(7))));
    -- not_parry <= not parry;

    -- sum_even <= (parry nand odd) and (not_parry nand even);
    -- sum_odd <= (parry nand even) and (not_parry nand odd);

    sum_even <= (xor d) xor even;
    sum_odd <= not sum_even;
end architecture;
