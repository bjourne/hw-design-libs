-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
--
-- Wallace tree multiplier.
-- Borrowed from https://vhdlguru.blogspot.com/2013/08/vhdl-code-for-wallace-tree.html
--
-- Should improve this to work with 8-bit operands.
library bjourne;
library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;
use bjourne.all;

entity wallace_tree is
    port  (
        a : in std_logic_vector(3 downto 0);
        b : in std_logic_vector(3 downto 0);
        c : out std_logic_vector(7 downto 0)
    );
end wallace_tree;

architecture rtl of wallace_tree is
    signal p0, p1, p2, p3 : std_logic_vector(6 downto 0);
    signal
        s11, s12, s13, s14, s15,
        s22, s23, s24, s25, s26,
        s32, s33, s34, s35, s36, s37 : std_logic;
    signal
        c11, c12, c13, c14, c15,
        c22, c23, c24, c25, c26,
        c32, c33, c34, c35, c36, c37 : std_logic;
begin
    muls0: for i in 0 to 3 generate
        p0(i) <= a(i) and b(0);
        p1(i) <= a(i) and b(1);
        p2(i) <= a(i) and b(2);
        p3(i) <= a(i) and b(3);
    end generate;

    -- First stage
    ha11: entity half_adder
        port map(
            p0(1),
            p1(0),
            s11,
            c11
        );
    fa12: entity full_adder
        port map(
            p0(2),
            p1(1),
            p2(0),
            s12,
            c12
        );
    fa13 : entity full_adder
        port map(
            p0(3),
            p1(2),
            p2(1),
            s13,
            c13
        );
    fa14: entity full_adder
        port map(
            p1(3),
            p2(2),
            p3(1),
            s14,
            c14
        );
    ha15: entity half_adder
        port map(
            p2(3),
            p3(2),
            s15,
            c15
        );

    -- Second stage
    ha22:  entity half_adder
        port map(
            c11,
            s12,
            s22,
            c22
        );
    fa23: entity full_adder
        port map(
            p3(0),
            c12,
            s13,
            s23,
            c23
        );
    fa24: entity full_adder
        port map(
            c13,c32,s14,s24,c24
        );
    fa25: entity full_adder port map(c14,c24,s15,s25,c25);
    fa26: entity full_adder port map(c15,c25,p3(3),s26,c26);

    -- Third stage
    ha32: entity half_adder
        port map(
            c22,
            s23,
            s32,
            c32
        );
    ha34: entity half_adder
        port map(c23,s24,s34,c34);
    ha35: entity half_adder
        port map(c34,s25,s35,c35);
    ha36: entity half_adder port map(c35,s26,s36,c36);
    ha37: entity half_adder port map(c36,c26,s37,c37);

    c(0) <= p0(0);
    c(1) <= s11;
    c(2) <= s22;
    c(3) <= s32;
    c(4) <= s34;
    c(5) <= s35;
    c(6) <= s36;
    c(7) <= s37;
end rtl;
