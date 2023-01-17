-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use bjourne.types.all;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.float_pkg.all;

entity invsqrt_f32 is
    port (
        clk, rstn : in std_logic;
        x : in float32;
        y : out float32
    );
end invsqrt_f32;

architecture rtl of invsqrt_f32 is
    -- Different types for different stages of the pipeline...
    signal s1_0 : unsigned(31 downto 0);
    signal s1_1 : float32;
    signal s2_0 : float32;
    signal s2_1 : unsigned(31 downto 0);
    signal s3_0 : float32;
    signal s3_1 : unsigned(31 downto 0);
    signal s4_0 : float32;
    signal s4_1 : unsigned(31 downto 0);
    signal s5_0 : float32;
begin
    y <= s5_0;
    process (clk)
    begin
        if rising_edge(clk) then
            if rstn = '0' then
                s1_0 <= to_unsigned(0, 32);
                s1_1 <= to_float(0.0);
                s2_0 <= to_float(0.0);
                s2_1 <= to_unsigned(0, 32);
                s3_0 <= to_float(0.0);
                s3_1 <= to_unsigned(0, 32);
                s4_0 <= to_float(0.0);
                s4_1 <= to_unsigned(0, 32);
                s5_0 <= to_float(0.0);
            else
                s1_0 <= 1597463174 - shift_right(unsigned(to_slv(x)), 1);
                s1_1 <= to_float(0.5) * x;
                s2_0 <= s1_1 * float32(std_logic_vector(s1_0));
                s2_1 <= s1_0;
                s3_0 <= s2_0 * float32(std_logic_vector(s2_1));
                s3_1 <= s2_1;
                s4_0 <= to_float(1.5) - s3_0;
                s4_1 <= s3_1;
                s5_0 <= float32(std_logic_vector(s4_1)) * s4_0;
            end if;
        end if;
    end process;
end architecture;
