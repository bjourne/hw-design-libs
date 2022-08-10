-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
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
    par <= xor (d & odd_even);
end architecture;
