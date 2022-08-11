-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use bjourne.all;

entity tb_dp_bram is
end tb_dp_bram;

architecture beh of tb_dp_bram is
    signal clk : std_logic;
    signal we_a, we_b : std_logic;
    signal addr_a, addr_b : natural;
    signal din_a, din_b : integer;
    signal dout_a, dout_b : integer;
    constant numbers : integer_vector(0 to 255) := (
        4, 2, 0, 17, 11, 18, 0, 15, 7, 4, 8, 2, 12, 7, 5, 17,
        11, 18, 14, 16, 16, 19, 9, 11, 15, 12, 17, 13, 3, 9, 4, 17,
        7, 19, 10, 12, 0, 7, 18, 5, 13, 13, 14, 19, 12, 17, 5, 15,
        6, 8, 7, 2, 6, 18, 1, 10, 7, 11, 14, 15, 10, 3, 10, 2,
        8, 15, 5, 7, 19, 3, 5, 9, 6, 17, 18, 14, 15, 17, 19, 7,
        15, 10, 7, 1, 3, 3, 10, 11, 13, 15, 2, 5, 19, 15, 0, 3,
        0, 11, 6, 5, 5, 6, 8, 9, 11, 2, 15, 11, 18, 11, 14, 12,
        8, 0, 3, 5, 14, 7, 6, 3, 12, 11, 4, 8, 5, 18, 10, 3,
        11, 10, 10, 12, 7, 2, 5, 8, 6, 12, 7, 3, 8, 18, 2, 10,
        8, 18, 19, 19, 1, 19, 13, 1, 13, 0, 18, 1, 6, 19, 11, 3,
        10, 19, 1, 13, 7, 19, 16, 1, 9, 13, 1, 17, 2, 19, 0, 0,
        14, 9, 11, 17, 16, 12, 14, 13, 7, 2, 2, 13, 17, 14, 8, 18,
        17, 18, 6, 4, 10, 2, 11, 2, 9, 12, 2, 2, 6, 9, 0, 15,
        15, 5, 18, 8, 10, 12, 5, 19, 19, 16, 8, 11, 1, 8, 9, 1,
        12, 18, 15, 16, 9, 14, 0, 18, 3, 15, 14, 15, 14, 2, 17, 1,
        3, 19, 14, 1, 19, 19, 5, 0, 17, 7, 3, 16, 13, 1, 5, 18
    );
    procedure tick(signal c : inout std_logic) is
    begin
        wait for 10 ns;
        c <= not c;
        wait for 10 ns;
        c <= not c;
    end;
    procedure test_collissions(
        signal clk0 : inout std_logic;
        signal addr_a0 : out integer;
        signal addr_b0 : out integer;
        signal we_a0 : out std_logic;
        signal we_b0 : out std_logic;
        signal din_a0 : out integer;
        signal din_b0 : out integer;
        signal dout_a0 : in integer
    ) is
    begin

        addr_a0 <= 0;
        we_a0 <= '1';
        din_a0 <= 1234;

        tick(clk0);
        assert dout_a = 1234;

        addr_a0 <= 10;
        din_a0 <= 4321;

        tick(clk0);
        assert dout_a = 4321;

        addr_a0 <= 0;
        we_a0 <= '0';
        tick(clk0);
        assert dout_a = 1234;

        -- Collissions

        addr_a0 <= 1;
        addr_b0 <= 1;
        din_a0 <= 5;
        din_b0 <= 20;
        we_a0 <= '1';
        tick(clk0);
        assert dout_a = 5;
        assert dout_b = 5;

        we_a0 <= '0';
        we_b0 <= '1';
        tick(clk0);
        assert dout_b = 20;
        assert dout_a = 20;

        -- B wins
        we_a0 <= '1';
        we_b0 <= '1';
        din_b0 <= 3;
        tick(clk0);
        assert dout_b = 3;
        assert dout_a = 3;

        we_a0 <= '1';
        we_b0 <= '0';
        for i in 0 to 255 loop
            addr_a0 <= i;
            din_a0 <= numbers(i);
            tick(clk0);
        end loop;

        we_a0 <= '0';
        for i in 0 to 255 loop
            addr_a0 <= i;
            tick(clk0);
            assert dout_a = numbers(i);
        end loop;
    end;
    procedure test_systolic(
        signal clk0 : inout std_logic;
        signal we_a0 : out std_logic;
        signal we_b0 : out std_logic;
        signal din_a0 : out integer;
        signal addr_a0 : out integer
    ) is
    begin
        we_a0 <= '1';
        we_b0 <= '0';
        for i in numbers'range loop
            addr_a0 <= i;
            din_a0 <= numbers(i);
            tick(clk0);
            report "i " & to_string(i);
        end loop;
    end;

begin
    dp_bram0: entity dp_bram
        generic map(
            DEPTH => 256 * 256
        )
        port map(
            clk_a => clk,
            clk_b => clk,
            we_a => we_a,
            we_b => we_b,
            addr_a => addr_a,
            addr_b => addr_b,
            din_a => din_a,
            din_b => din_b,
            dout_a => dout_a,
            dout_b => dout_b
        );

    process
    begin
        clk <= '0';
        tick(clk);
        test_collissions(
            clk,
            addr_a, addr_b,
            we_a, we_b,
            din_a, din_b,
            dout_a);
        test_systolic(
            clk,
            we_a, we_b,
            din_a,
            addr_a
        );

        assert false report "all tests passed" severity note;
        wait;

    end process;

end architecture;
