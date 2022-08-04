-- [[14  5  3  9 11 17]
--  [18  9  8 18  3 17]
--  [11  0 10 17  5 12]
--  [19 16  2 19  2 19]
--  [19 14 15 18  6 10]
--  [13 19 19  2  2 19]]
-- [[18  7 13 14  4  5]
--  [ 1 15 14 19 12 10]
--  [ 7 13 18  0  2  3]
--  [13 13  1 18 16 13]
--  [ 0  6  9  5 13 10]
--  [15 19 13 13 16  7]]
-- [[ 650  718  635  729  681  475]
--  [ 878  940  770  983  795  587]
--  [ 669  686  541  641  593  440]
--  [ 904 1019  791 1169  906  661]
--  [ 845  998  915 1016  800  644]
--  [ 697 1022 1044  836  680  491]]

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
    signal a_row3, b_col3, c_row3 : integer_vector(0 to 2);

    signal in_valid4, in_ready4 : std_logic;
    signal a_row4, b_col4, c_row4 : integer_vector(0 to 3);

    signal in_valid5, in_ready5 : std_logic;
    signal a_row5, b_col5, c_row5 : integer_vector(0 to 4);

    signal in_valid6, in_ready6 : std_logic;
    signal a_row6, b_col6, c_row6 : integer_vector(0 to 5);


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

    procedure test6x6(signal clk0 : inout std_logic;
                      signal in_valid : inout std_logic;
                      signal in_ready : in std_logic;
                      signal a_row : out integer_vector(0 to 5);
                      signal b_col : out integer_vector(0 to 5);
                      signal c_row : in integer_vector(0 to 5)) is
    begin
        assert in_ready = '1';
        in_valid <= '1';

        -- Tick 0
        a_row <= (14,  5,  3,  9, 11, 17);
        b_col <= (18,  1,  7, 13,  0, 15);
        tick(clk0);

        -- Tick 1
        a_row <= (18,  9,  8, 18,  3, 17);
        b_col <= ( 7, 15, 13, 13,  6, 19);
        tick(clk0);

        -- Tick 2
        a_row <= (11,  0, 10, 17,  5, 12);
        b_col <= (13, 14, 18,  1,  9, 13);
        tick(clk0);

        -- Tick 3
        a_row <= (19, 16,  2, 19,  2, 19);
        b_col <= (14, 19,  0, 18,  5, 13);
        tick(clk0);

        -- Tick 4
        a_row <= (19, 14, 15, 18,  6, 10);
        b_col <= ( 4, 12,  2, 16, 13, 16);
        tick(clk0);

        -- Tick 5
        a_row <= (13, 19, 19,  2,  2, 19);
        b_col <= ( 5, 10,  3, 13, 10,  7);
        tick(clk0);

        -- Tick 6
        tick(clk0);

        -- Tick 7
        tick(clk0);

        -- Tick 8
        tick(clk0);

        -- Tick 9
        tick(clk0);

        -- Tick 10
        tick(clk0);

        -- Tick 11
        assert c_row = (650, 718, 635, 729, 681, 475);
        tick(clk0);

        -- Tick 12
        assert c_row = (878, 940, 770, 983, 795, 587);
        tick(clk0);

        -- Tick 13
        assert c_row = (669, 686, 541, 641, 593, 440);
        tick(clk0);

        -- Tick 14
        assert c_row = (904, 1019, 791, 1169, 906, 661);
        tick(clk0);

        -- Tick 15
        assert c_row = (845, 998, 915, 1016, 800, 644);
        tick(clk0);

        -- Tick 16
        assert c_row = (697, 1022, 1044, 836, 680, 491);
        tick(clk0);

        assert in_ready = '1';
    end procedure;

    procedure test3x3(signal clk0 : inout std_logic;
                      signal in_valid : inout std_logic;
                      signal in_ready : in std_logic;
                      signal a_row : inout integer_vector(0 to 2);
                      signal b_col : inout integer_vector(0 to 2);
                      signal c_row : in integer_vector(0 to 2)) is
    begin
        assert in_ready = '1';
        in_valid <= '1';
        -- Tick 0
        a_row <= (15, 2, 3);
        b_col <= (10, 13, 16);
        tick(clk0);

        -- Tick 1
        assert in_ready3 = '0';
        in_valid <= '0';
        a_row <= (4, 5, 6);
        b_col <= (11, 14, 17);
        tick(clk0);

        -- Tick 2
        a_row <= (7, 8, 9);
        b_col <= (12, 15, 18);
        tick(clk0);

        -- Tick 3
        a_row <= (0, 0, 0);
        b_col <= (0, 0, 0);
        tick(clk0);

        -- Tick 4
        tick(clk0);

        -- Tick 5
        assert c_row = (224, 244, 264);
        tick(clk0);

        -- Tick 6
        assert c_row = (201, 216, 231);
        tick(clk0);

        -- Tick 7
        assert c_row = (318, 342, 366);
        tick(clk0);

        assert in_ready = '1';

    end;

    procedure test4x4(signal clk0 : inout std_logic;
                      signal in_valid : inout std_logic;
                      signal in_ready : in std_logic;
                      signal a_row : out integer_vector(0 to 3);
                      signal b_col : out integer_vector(0 to 3);
                      signal c_row : in integer_vector(0 to 3)) is
    begin
        assert in_ready = '1';
        in_valid <= '1';

        a_row <= (3, 6, 9, 0);
        b_col <= (9, 2, 4, 4);
        tick(clk0);

        -- Tick 1
        assert in_ready = '0';
        in_valid <= '0';

        a_row <= (4, 5, 8, 6);
        b_col <= (7, 2, 2, 7);
        tick(clk0);

        -- Tick 2
        a_row <= (0, 6, 8, 5);
        b_col <= (5, 7, 8, 0);
        tick(clk0);

        -- Tick 3
        a_row <= (9, 7, 4, 9);
        b_col <= (6, 7, 3, 8);
        tick(clk0);

        -- Tick 4
        tick(clk0);

        -- Tick 5
        tick(clk0);

        -- Tick 6
        tick(clk0);

        -- Tick 7
        assert c_row = (75, 51, 129, 87);
        tick(clk0);

        -- Tick 8
        assert c_row = (102, 96, 119, 131);
        tick(clk0);

        -- Tick 9
        assert c_row = (64, 63, 106, 106);
        tick(clk0);

        -- Tick 10
        assert c_row = (147, 148, 126, 187);
        tick(clk0);

        assert in_ready = '1';
    end;
    procedure test5x5(signal clk0 : inout std_logic;
                      signal in_valid : inout std_logic;
                      signal in_ready : in std_logic;
                      signal a_row : out integer_vector(0 to 4);
                      signal b_col : out integer_vector(0 to 4);
                      signal c_row : in integer_vector(0 to 4)) is
    begin
        assert in_ready = '1';
        in_valid <= '1';

        -- Tick 0
        a_row <= (7, 7, 0, 1, 1);
        b_col <= (7, 1, 4, 0, 0);
        tick(clk0);

        -- Tick 1
        in_valid <= '0';
        a_row <= (3, 1, 6, 1, 5);
        b_col <= (7, 9, 1, 0, 6);
        tick(clk0);

        -- Tick 2
        a_row <= (4, 6, 2, 6, 6);
        b_col <= (5, 8, 6, 8, 3);
        tick(clk0);

        -- Tick 3
        a_row <= (4, 1, 0, 2, 6);
        b_col <= (9, 7, 2, 9, 6);
        tick(clk0);

        -- Tick 4
        a_row <= (6, 9, 5, 2, 4);
        b_col <= (4, 0, 5, 4, 0);
        tick(clk0);

        -- Tick 5
        tick(clk0);

        -- Tick 6
        tick(clk0);

        -- Tick 7
        tick(clk0);

        -- Tick 8
        tick(clk0);

        -- Tick 9
        assert c_row = (56, 118, 102, 127, 32);
        tick(clk0);

        -- Tick 10
        assert c_row = (46, 66, 82, 85, 46);
        tick(clk0);

        -- Tick 11
        assert c_row = (42, 120, 146, 172, 50);
        tick(clk0);

        -- Tick 12
        assert c_row = (29, 73, 62, 97, 24);
        tick(clk0);

        -- Tick 13
        assert c_row = (71, 152, 160, 169, 57);
        tick(clk0);

        assert in_ready = '1';
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
            c_row => c_row3
        );
    systolic4: entity systolic
        generic map(
            N => 4
        )
        port map (
            clk => clk,
            rstn => rstn,
            in_valid => in_valid4,
            in_ready => in_ready4,
            a_row => a_row4,
            b_col => b_col4,
            c_row => c_row4
        );
    systolic5: entity systolic
        generic map(
            N => 5
        )
        port map (
            clk => clk,
            rstn => rstn,
            in_valid => in_valid5,
            in_ready => in_ready5,
            a_row => a_row5,
            b_col => b_col5,
            c_row => c_row5
        );
    systolic6: entity systolic
        generic map(
            N => 6
        )
        port map (
            clk => clk,
            rstn => rstn,
            in_valid => in_valid6,
            in_ready => in_ready6,
            a_row => a_row6,
            b_col => b_col6,
            c_row => c_row6
        );
    process
    begin
        a_row3 <= (-1, -1, -1);
        b_col3 <= (-1, -1, -1);
        a_row4 <= (-1, -1, -1, -1);
        b_col4 <= (-1, -1, -1, -1);
        a_row5 <= (-1, -1, -1, -1, -1);
        b_col5 <= (-1, -1, -1, -1, -1);
        a_row6 <= (others => -1);
        b_col6 <= (others => -1);
        reset(clk, rstn);

        test3x3(clk, in_valid3, in_ready3, a_row3, b_col3, c_row3);
        test4x4(clk, in_valid4, in_ready4, a_row4, b_col4, c_row4);
        test5x5(clk, in_valid5, in_ready5, a_row5, b_col5, c_row5);
        test6x6(clk, in_valid6, in_ready6, a_row6, b_col6, c_row6);

        assert false report "all tests passed" severity note;
        wait;
    end process;
end architecture;
