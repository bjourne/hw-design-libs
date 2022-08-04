-- [[3 6 9 0]
--  [4 5 8 6]
--  [0 6 8 5]
--  [9 7 4 9]]
-- [[9 7 5 6]
--  [2 2 7 7]
--  [4 2 8 3]
--  [4 7 0 8]]
-- [[ 75  51 129  87]
--  [102  96 119 131]
--  [ 64  63 106 106]
--  [147 148 126 187]]

-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use bjourne.all;

entity tb_systolic is
end tb_systolic;

architecture beh of tb_systolic is
    signal clk : std_logic;
    signal rstn : std_logic;
    signal in_valid3, in_ready3 : std_logic;
    signal a_row3, b_col3, c_out3 : integer_vector(0 to 2);

    signal in_valid4, in_ready4 : std_logic;
    signal a_row4, b_col4, c_out4 : integer_vector(0 to 3);

    procedure tick(signal c : inout std_logic) is
    begin
        wait for 10 ns;
        c <= not c;
        wait for 10 ns;
        c <= not c;
    end;

    procedure reset(signal clk0 : inout std_logic;
                    signal rstn0 : inout std_logic) is
    begin
        clk0 <= '0';
        rstn0 <= '0';
        wait for 10 ns;
        tick(clk0);

        rstn0 <= '1';
        tick(clk0);
    end;
begin
    systolic3: entity systolic
        generic map(
            N => 3
        )
        port map (
            clk => clk,
            rstn => rstn,
            in_valid => in_valid3,
            in_ready => in_ready3,
            a_row => a_row3,
            b_col => b_col3,
            c_out => c_out3
        );
    -- systolic4: entity systolic
    --     generic map(
    --         N => 4
    --     )
    --     port map (
    --         clk => clk,
    --         rstn => rstn,
    --         in_valid => in_valid4,
    --         in_ready => in_ready4,
    --         a_row => a_row4,
    --         b_col => b_col4,
    --         c_out => c_out4
    --     );
    process
    begin
        a_row3 <= (-1, -1, -1);
        b_col3 <= (-1, -1, -1);
        a_row4 <= (-1, -1, -1, -1);
        b_col4 <= (-1, -1, -1, -1);
        reset(clk, rstn);


        -- assert in_ready4 = '1';
        -- in_valid4 <= '1';

        -- a_row4 <= (3, 6, 9, 0);
        -- b_col4 <= (9, 2, 4, 4);
        -- tick(clk);

        -- a_row4 <= (4, 5, 8, 6);
        -- b_col4 <= (7, 2, 2, 7);
        -- tick(clk);


        assert in_ready3 = '1';
        in_valid3 <= '1';
        -- Tick 0
        a_row3 <= (15, 2, 3);
        b_col3 <= (10, 13, 16);
        tick(clk);

        -- Tick 1
        assert in_ready3 = '0';
        in_valid3 <= '0';
        a_row3 <= (4, 5, 6);
        b_col3 <= (11, 14, 17);
        tick(clk);

        -- Tick 2
        a_row3 <= (7, 8, 9);
        b_col3 <= (12, 15, 18);
        tick(clk);

        -- Tick 3
        a_row3 <= (0, 0, 0);
        b_col3 <= (0, 0, 0);
        tick(clk);

        -- Tick 4
        tick(clk);

        -- Tick 5
        assert c_out3 = (224, 244, 264);
        tick(clk);

        -- Tick 6
        assert c_out3 = (201, 216, 231);
        tick(clk);

        -- Tick 7
        assert c_out3 = (318, 342, 366);
        assert in_ready3 = '1';
        tick(clk);

        assert false report "all tests passed" severity note;
        wait;
    end process;
end architecture;
