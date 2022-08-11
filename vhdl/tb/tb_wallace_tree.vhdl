-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use bjourne.all;

entity tb_wallace_tree is
end tb_wallace_tree;

architecture beh of tb_wallace_tree is
    signal a, b : std_logic_vector(3 downto 0);
    signal c : std_logic_vector(7 downto 0);
begin
    wallace0: entity wallace_tree
        port map(
            a => a,
            b => b,
            c => c
        );
    process
    begin
        a <= std_logic_vector(to_signed(3, a'length));
        b <= std_logic_vector(to_signed(3, b'length));
        wait for 10 ns;
        assert to_integer(signed(c)) = 9;

        a <= std_logic_vector(to_signed(7, a'length));
        b <= std_logic_vector(to_signed(3, b'length));
        wait for 10 ns;
        assert to_integer(signed(c)) = 21;

        a <= std_logic_vector(to_signed(7, a'length));
        b <= std_logic_vector(to_signed(-2, b'length));
        wait for 10 ns;
        report "c is " & to_string(c);
        --assert to_integer(signed(c)) = -14;




        assert false report "all tests passed" severity note;
        wait;
    end process;
end architecture;
