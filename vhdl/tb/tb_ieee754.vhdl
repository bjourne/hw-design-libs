-- Copyright (C) 2022 Björn A. Lindqvist <bjourne@gmail.com>
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
library work;
use work.all;
use work.ieee754.all;

entity tb_ieee754 is
end tb_ieee754;

architecture beh of tb_ieee754 is
    -- Little endian.
    constant fp_p100 : std_logic_vector(31 downto 0) := X"42c80000";
    constant fp_n100 : std_logic_vector(31 downto 0) := X"c2c80000";
    constant fp_1 : std_logic_vector(31 downto 0) := X"3f800000";
    constant fp_0 : std_logic_vector(31 downto 0) := X"00000000";
    constant fp_0_2 : std_logic_vector(31 downto 0) := X"3e4ccccd";
    constant fp_120_000 : std_logic_vector(31 downto 0) := X"47ea6000";

    constant fp_59_000_000 : std_logic_vector(31 downto 0) := X"4c611130";

    -- Extra large and small numbers.
    -- -2_123_000_000
    constant fp_n2bill : std_logic_vector(31 downto 0) := X"cefd14d2";
begin
    process
    begin
        assert float32_to_int32(fp_p100) = 100;
        assert float32_to_int32(fp_n100) = -100;
        assert float32_to_int32(fp_1) = 1;
        assert float32_to_int32(fp_0) = 0;
        assert float32_to_int32(fp_0_2) = 0;
        assert float32_to_int32(fp_120_000) = 120_000;
        assert float32_to_int32(fp_59_000_000) = 59_000_000;
        assert float32_to_int32(fp_n2bill) = -2_123_000_064;
        assert false report "done" severity note;
        wait;
    end process;
end beh;
