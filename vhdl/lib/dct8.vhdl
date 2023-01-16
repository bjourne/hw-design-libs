library bjourne;
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;

entity dct8 is
    port(
        clk, rstn : in std_logic;
        x : in real_vector(0 to 7);
        y : out real_vector(0 to 7)
    );
end dct8;

architecture rtl of dct8 is
    constant C1_A : real := -0.7856949583;
    constant C1_B : real := -1.1758756024;
    constant C1_C : real :=  0.9807852804;
    constant C3_A : real := -0.2758993792;
    constant C3_B : real := -1.3870398453;
    constant C3_C : real :=  0.8314696123;
    constant C6_A : real :=  0.7653668647;
    constant C6_B : real := -1.8477590650;
    constant C6_C : real :=  0.5411961001;
    constant NRM1 : real :=  0.3535533905;
    constant NRM2 : real :=  0.5;

    -- First stage registers
    signal s1 : real_vector(0 to 7);
    signal s2 : real_vector(0 to 9);
    signal s3 : real_vector(0 to 10);
    signal s4 : real_vector(0 to 8);
    signal s5 : real_vector(0 to 7);
    signal s6 : real_vector(0 to 7);
    signal s7 : real_vector(0 to 7);
begin
    process(clk)
    begin
        if rising_edge(clk) then
            if rstn = '0' then
                s1 <= (others => 0.0);
                s2 <= (others => 0.0);
                s3 <= (others => 0.0);
                s4 <= (others => 0.0);
                s5 <= (others => 0.0);
                s6 <= (others => 0.0);
                s7 <= (others => 0.0);
            else
                s1(0)  <= x(0) + x(7);
                s1(1)  <= x(3) + x(4);
                s1(2)  <= x(1) + x(6);
                s1(3)  <= x(2) + x(5);
                s1(4)  <= x(3) - x(4);
                s1(5)  <= x(0) - x(7);
                s1(6)  <= x(1) - x(6);
                s1(7)  <= x(2) - x(5);
                s2(0)  <= s1(0) + s1(1);
                s2(1)  <= s1(2) + s1(3);
                s2(2)  <= -1.38703984532 * s1(4);
                s2(3)  <= s1(4) + s1(5);
                s2(4)  <= -0.78569495838 * s1(6);
                s2(5)  <= s1(7) + s1(6);
                s2(6)  <= -0.27589937928 * s1(5);
                s2(7)  <= -1.17587560241 * s1(7);
                s2(8)  <= s1(0) - s1(1);
                s2(9)  <= s1(2) - s1(3);
                s3(0)  <= s2(0) + s2(1);
                s3(1)  <= 0.8314696123 * s2(3);
                s3(2)  <= 0.9807852804 * s2(5);
                s3(3)  <= 0.76536686473 * s2(8);
                s3(4)  <= s2(9) + s2(8);
                s3(5)  <= s2(0) - s2(1);
                s3(6)  <= -1.84775906502 * s2(9);
                s3(7)  <= s2(2);
                s3(8)  <= s2(4);
                s3(9)  <= s2(6);
                s3(10) <= s2(7);
                s4(0)  <= 0.35355339059 * s3(0);
                s4(1)  <= s3(7) + s3(1);
                s4(2)  <= s3(8) + s3(2);
                s4(3)  <= s3(9) + s3(1);
                s4(4)  <= s3(10) + s3(2);
                s4(5)  <= 0.54119610014 * s3(4);
                s4(6)  <= 0.35355339059 * s3(5);
                s4(7)  <= s3(3);
                s4(8)  <= s3(6);
                s5(0)  <= s4(1) + s4(2);
                s5(1)  <= s4(3) + s4(4);
                s5(2)  <= s4(7) + s4(5);
                s5(3)  <= s4(1) - s4(2);
                s5(4)  <= s4(3) - s4(4);
                s5(5)  <= s4(8) + s4(5);
                s5(6)  <= s4(0);
                s5(7)  <= s4(6);
                s6(0)  <= s5(0) + s5(1);
                s6(1)  <= 0.35355339059 * s5(2);
                s6(2)  <= 0.5 * s5(3);
                s6(3)  <= 0.5 * s5(4);
                s6(4)  <= 0.35355339059 * s5(5);
                s6(5)  <= s5(0) - s5(1);
                s6(6)  <= s5(6);
                s6(7)  <= s5(7);
                s7(0)  <= 0.35355339059 * s6(0);
                s7(1)  <= 0.35355339059 * s6(5);
                s7(2)  <= s6(6);
                s7(3)  <= s6(1);
                s7(4)  <= s6(2);
                s7(5)  <= s6(7);
                s7(6)  <= s6(3);
                s7(7)  <= s6(4);
                y      <= (s7(2), s7(0), s7(3), s7(4), s7(5), s7(6), s7(7), s7(1));
            end if;
        end if;
    end process;
end architecture;
