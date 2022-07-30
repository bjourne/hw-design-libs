-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use bjourne.all;

entity tb_parity is
end tb_parity;

architecture beh of tb_parity is
    signal bits : std_logic_vector(7 downto 0);
    signal even : std_logic;
    signal odd : std_logic;
    signal sum_even : std_logic;
    signal sum_odd : std_logic;
begin
    parity0: entity parity
        port map (
            d => bits,
            even => even,
            odd => odd,
            sum_even => sum_even,
            sum_odd => sum_odd
        );

    process
    begin
        bits <= "00000000";
        even <= '1';
        odd <= '0';
        wait for 10 ns;
        assert sum_even = '1';
        assert sum_odd = '0';

        bits <= "00000001";
        wait for 10 ns;
        assert sum_even = '0';
        assert sum_odd = '1';

        bits <= "00000111";
        wait for 10 ns;
        assert sum_even = '0';
        assert sum_odd = '1';

        -- Sum even with even=0
        even <= '0';
        odd <= '1';
        bits <= "00000000";
        wait for 10 ns;
        assert sum_even = '0';
        assert sum_odd = '1';

        bits <= "00000001";
        wait for 10 ns;
        assert sum_even = '1';
        assert sum_odd = '0';


        assert false report "all tests passed" severity note;
        wait;
    end process;
end beh;
