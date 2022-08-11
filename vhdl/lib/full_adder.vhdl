library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;

entity full_adder is
    Port ( a : in std_logic;
           b : in std_logic;
           ci : in std_logic;
           s : out std_logic;
           co : out std_logic);
end full_adder;
architecture rtl of full_adder is
begin
    s <= (a xor b xor ci);
    co <= (a and b) xor (ci and (a xor b));
end rtl;
