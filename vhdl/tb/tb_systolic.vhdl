-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use bjourne.all;

entity tb_systolic is
end tb_systolic;

architecture beh of tb_systolic is

    -- 2d arrays are annoying in vhdl
    constant mat_a_3x3 : integer_vector(0 to 8) := (
        15, 2, 3,
        4, 5, 6,
        7, 8, 9
    );
    constant mat_b_3x3 : integer_vector(0 to 8) := (
        10, 11, 12,
        13, 14, 15,
        16, 17, 18
    );
    constant mat_c_3x3 : integer_vector(0 to 8) := (
        224, 244, 264,
        201, 216, 231,
        318, 342, 366
    );
    constant mat_a_4x4 : integer_vector(0 to 15) := (
        4, 9, 3, 3,
        9, 4, 14, 9,
        11, 17, 19, 10,
        1, 19, 1, 5
    );
    constant mat_b_4x4 : integer_vector(0 to 15) := (
        14, 12, 17, 19,
        15, 1, 14, 6,
        8, 18, 1, 6,
        15, 6, 9, 2
    );
    constant mat_c_4x4 : integer_vector(0 to 15) := (
        260, 129, 224, 154,
        433, 418, 304, 297,
        711, 551, 534, 445,
        382, 79, 329, 149
    );
    constant mat_a_5x5 : integer_vector(0 to 24) := (
        8, 8, 1, 3, 0,
        6, 0, 19, 7, 5,
        13, 10, 18, 15, 2,
        5, 1, 0, 1, 15,
        2, 8, 8, 8, 18
    );
    constant mat_b_5x5 : integer_vector(0 to 24) := (
        6, 17, 0, 11, 10,
        1, 18, 3, 12, 15,
        15, 14, 2, 15, 7,
        9, 9, 15, 4, 5,
        13, 14, 17, 8, 9
    );
    constant mat_c_5x5 : integer_vector(0 to 24) := (
        98, 321, 71, 211, 222,
        449, 501, 228, 419, 273,
        519, 816, 325, 609, 499,
        235, 322, 273, 191, 205,
        446, 614, 466, 414, 398
    );
    constant mat_a_6x6 : integer_vector(0 to 35) := (
        0, 2, 3, 19, 18, 15,
        4, 0, 10, 5, 12, 17,
        1, 7, 16, 5, 1, 16,
        9, 11, 8, 16, 3, 6,
        4, 3, 17, 10, 10, 7,
        2, 2, 10, 11, 17, 13
    );
    constant mat_b_6x6 : integer_vector(0 to 35) := (
        11, 12, 9, 19, 11, 13,
        11, 3, 9, 10, 5, 12,
        6, 11, 17, 2, 13, 6,
        8, 3, 6, 10, 4, 12,
        6, 7, 12, 13, 14, 19,
        1, 4, 4, 18, 19, 16
    );
    constant mat_c_6x6 : integer_vector(0 to 35) := (
        315, 282, 459, 720, 662, 852,
        233, 325, 448, 608, 685, 672,
        246, 295, 450, 472, 592, 528,
        420, 322, 472, 604, 478, 642,
        326, 372, 560, 496, 593, 612,
        307, 344, 528, 643, 691, 773
    );
    constant mat_a_7x7 : integer_vector(0 to 48) := (
        10, 0, 12, 17, 9, 19, 12,
        15, 17, 2, 0,  7,  1,  3,
        9, 19, 15, 11, 15, 16, 13,
        7, 6, 19, 0, 11, 19, 14,
        5, 4, 19, 0, 2, 1, 9,
        6, 2, 14, 8, 10, 16, 8,
        12, 7, 2, 14, 19, 19, 1
    );
    constant mat_b_7x7 : integer_vector(0 to 48) := (
        16, 6, 16, 0, 9, 0, 2,
        9, 18, 17, 16, 13, 15, 2,
        15, 9, 11, 19, 18, 17, 0,
        19, 5, 12, 1, 5, 7, 0,
        19, 12, 5, 2, 1, 19, 3,
        8, 17, 0, 5, 12, 13, 19,
        19, 10, 11, 17, 1, 4, 16
    );
    constant mat_c_7x7 : integer_vector(0 to 48) := (
        1214, 804, 673, 562, 640, 789, 600,
        621, 545, 619, 380, 414, 447, 152,
        1409, 1168, 982, 931, 873, 1162, 613,
        1078, 916, 632, 812, 736, 925, 644,
        618, 404, 466, 587, 462, 470, 187,
        946, 710, 518, 542, 582, 754, 478,
        1083, 847, 607, 314, 553, 849, 472
    );

    constant mat_a_16x16 : integer_vector(0 to 255) := (
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
    constant mat_b_16x16 : integer_vector(0 to 255) := (
        2, 11, 8, 5, 16, 9, 10, 4, 3, 3, 4, 10, 0, 1, 6, 10,
        14, 18, 6, 16, 6, 9, 2, 16, 6, 2, 13, 6, 0, 13, 13, 10,
        5, 1, 11, 11, 5, 17, 3, 14, 7, 5, 11, 2, 1, 19, 7, 7,
        12, 1, 10, 9, 1, 1, 17, 18, 11, 4, 17, 2, 19, 8, 0, 9,
        14, 18, 5, 9, 12, 14, 0, 6, 1, 14, 9, 11, 18, 11, 17, 15,
        11, 15, 11, 3, 16, 15, 14, 12, 6, 13, 3, 17, 3, 2, 7, 8,
        9, 12, 6, 11, 4, 2, 17, 16, 13, 9, 9, 12, 4, 6, 9, 17,
        14, 9, 5, 15, 6, 1, 19, 9, 8, 14, 8, 14, 4, 6, 17, 16,
        19, 9, 8, 17, 7, 9, 0, 1, 8, 3, 6, 7, 4, 0, 2, 5,
        9, 18, 17, 14, 0, 3, 19, 15, 5, 8, 4, 9, 4, 10, 10, 6,
        11, 16, 7, 7, 18, 0, 6, 12, 1, 6, 1, 0, 16, 18, 11, 13,
        5, 18, 12, 6, 1, 0, 10, 17, 5, 16, 4, 17, 14, 10, 15, 10,
        17, 15, 18, 17, 1, 3, 10, 8, 7, 1, 4, 19, 5, 14, 5, 10,
        3, 11, 11, 15, 13, 2, 12, 14, 8, 16, 1, 15, 3, 18, 13, 16,
        10, 8, 7, 7, 4, 17, 17, 14, 5, 1, 8, 8, 7, 8, 19, 17,
        19, 13, 2, 18, 0, 0, 15, 7, 11, 3, 4, 0, 4, 3, 3, 13
    );
    constant mat_c_16x16 : integer_vector(0 to 255) := (
        1667, 1517, 1108, 1476, 921, 720, 1558, 1351, 896, 995, 841, 1215, 1019, 1002, 1087, 1483,
        2290, 2509, 1722, 2246, 1528, 1319, 2009, 2328, 1312, 1562, 1402, 1697, 1443, 1816, 1862, 2214,
        1986, 2326, 1729, 2230, 1117, 873, 1996, 2313, 1341, 1345, 1197, 1687, 1151, 1823, 1671, 2067,
        1392, 1743, 1285, 1304, 1010, 915, 1369, 1515, 710, 1051, 727, 1368, 894, 1219, 1384, 1395,
        1969, 2453, 1717, 2087, 1292, 1136, 1895, 2167, 1034, 1396, 1133, 1765, 1408, 1976, 2088, 2208,
        1390, 1669, 1376, 1709, 872, 712, 1391, 1379, 896, 948, 761, 1481, 539, 1232, 1190, 1423,
        1732, 1798, 1292, 1744, 918, 810, 1484, 1647, 964, 977, 877, 1368, 992, 1464, 1444, 1722,
        1167, 1458, 1116, 1289, 913, 806, 1225, 1269, 715, 1030, 657, 1247, 836, 1072, 1217, 1367,
        1347, 1511, 1218, 1614, 903, 701, 1409, 1513, 893, 964, 875, 1136, 796, 1344, 1176, 1477,
        1721, 1767, 1510, 1803, 1437, 1262, 1640, 2114, 1175, 1116, 1232, 1363, 1041, 1745, 1433, 1867,
        1387, 1954, 1429, 1556, 1097, 871, 1590, 1914, 1020, 1343, 993, 1640, 908, 1285, 1398, 1589,
        2068, 2169, 1630, 2135, 1197, 1140, 2057, 2093, 1336, 1431, 1315, 1865, 1271, 1632, 1705, 2209,
        1378, 1630, 1049, 1576, 846, 768, 1198, 1316, 849, 788, 852, 1056, 581, 1056, 1077, 1375,
        1667, 1845, 1518, 1778, 1243, 1234, 1700, 1786, 1010, 1334, 1100, 1547, 1000, 1411, 1637, 1742,
        1929, 2193, 1770, 1904, 1227, 1302, 1998, 2254, 1060, 1290, 1336, 1722, 1300, 1817, 1925, 1995,
        1989, 2172, 1420, 1864, 1020, 1298, 1286, 1696, 1006, 1148, 1065, 1522, 995, 1379, 1468, 1640
    );

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

    signal in_valid7, in_ready7 : std_logic;
    signal a_row7, b_col7, c_row7 : integer_vector(0 to 6);

    signal in_valid16, in_ready16 : std_logic;
    signal a_row16, b_col16, c_row16 : integer_vector(0 to 15);

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

    procedure test_matmul(size : positive;
                          mat_a : integer_vector;
                          mat_b : integer_vector;
                          mat_c : integer_vector;
                          signal clk0 : inout std_logic;
                          signal in_valid : inout std_logic;
                          signal in_ready : in std_logic;
                          signal a_row : out integer_vector;
                          signal b_col : out integer_vector;
                          signal c_row : in integer_vector) is
    begin
        assert in_ready = '1';
        in_valid <= '1';

        -- Tick 0 to 6
        for pass in 0 to size - 1 loop
            if pass > 0 then
                assert in_ready = '0';
                in_valid <= '0';
            end if;
            for i in 0 to size - 1 loop
                a_row(i) <= mat_a(size * pass + i);
                b_col(i) <= mat_b(size * i + pass);
            end loop;
            tick(clk0);
        end loop;

        -- Tick 7 to 12
        for pass in 0 to size - 2 loop
            tick(clk0);
        end loop;

        -- Tick 13 to 19
        for pass in 0 to size - 1 loop
            for i in 0 to size - 1 loop
                assert c_row(i) = mat_c(size * pass + i);
            end loop;
            tick(clk0);
        end loop;
        assert in_ready = '1';
    end procedure;
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
    systolic7: entity systolic
        generic map(
            N => 7
        )
        port map (
            clk => clk,
            rstn => rstn,
            in_valid => in_valid7,
            in_ready => in_ready7,
            a_row => a_row7,
            b_col => b_col7,
            c_row => c_row7
        );
    systolic16: entity systolic
        generic map(
            N => 16
        )
        port map (
            clk => clk,
            rstn => rstn,
            in_valid => in_valid16,
            in_ready => in_ready16,
            a_row => a_row16,
            b_col => b_col16,
            c_row => c_row16
        );
    process
    begin
        reset(clk, rstn);
        test_matmul(3, mat_a_3x3, mat_b_3x3, mat_c_3x3,
                    clk, in_valid3, in_ready3, a_row3, b_col3, c_row3);
        test_matmul(4, mat_a_4x4, mat_b_4x4, mat_c_4x4,
                    clk, in_valid4, in_ready4, a_row4, b_col4, c_row4);
        test_matmul(5, mat_a_5x5, mat_b_5x5, mat_c_5x5,
                    clk, in_valid5, in_ready5, a_row5, b_col5, c_row5);
        test_matmul(6, mat_a_6x6, mat_b_6x6, mat_c_6x6,
                    clk, in_valid6, in_ready6, a_row6, b_col6, c_row6);
        test_matmul(7, mat_a_7x7, mat_b_7x7, mat_c_7x7,
                    clk, in_valid7, in_ready7, a_row7, b_col7, c_row7);
        test_matmul(16, mat_a_16x16, mat_b_16x16, mat_c_16x16,
                    clk, in_valid16, in_ready16, a_row16, b_col16, c_row16);
        assert false report "all tests passed" severity note;
        wait;
    end process;
end architecture;
