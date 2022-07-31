-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use bjourne.all;

entity tb_parity is
end tb_parity;

architecture beh of tb_parity is
    signal d : std_logic_vector(7 downto 0);
    signal odd_even : std_logic;
    signal par : std_logic;
    -- signal odd : std_logic;
    -- signal sum_even : std_logic;
    -- signal sum_odd : std_logic;
begin
    parity0: entity parity
        port map (
            d => d,
            odd_even => odd_even,
            par => par
        );

    process
    begin
        d <= "00000000";
        odd_even <= '1';
        wait for 10 ns;
        assert par = '1';

        odd_even <= '0';
        wait for 10 ns;
        assert par = '0';

        d <= "00000001";
        wait for 10 ns;
        assert par = '1';

        d <= "00000111";
        wait for 10 ns;
        assert par = '1';

        assert false report "all tests passed" severity note;
        wait;
    end process;
end beh;
