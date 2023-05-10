-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library bjourne_pl;
library ieee;
use ieee.numeric_std.all;
use ieee.std_logic_1164.all;
use std.textio.all;
use bjourne.all;
use bjourne.utils.all;
use bjourne.types.all;

entity tb_histogram2 is
end tb_histogram2;


architecture beh of tb_histogram2 is
    procedure write_port(l0 : inout line;
                         r : std_logic;
                         v : std_logic;
                         d : integer) is
    begin
        write(l0, string'("   "));
        io.write_bool(l0, r);
        io.write_bool(l0, v);
        io.write_int(l0, d);
    end procedure;

    procedure write_ports(i : integer;
                          r : std_logic_vector;
                          v : std_logic_vector;
                          d : integer_vector) is
        variable l0 : line;
    begin
        io.write_int(l0, i);
        for k in r'range loop
            if k > 0 then
                write(l0, string'(" "));
            end if;
            write_port(l0, r(k), v(k), d(k));
        end loop;
        writeline(output, l0);
    end procedure;

    procedure debug_adder(line0 : inout line; x0_r : std_logic) is
    begin
        io.write_bool(line0, x0_r);
    end procedure;

    signal clk, nrst : std_logic;

    -- First upstream
    signal x0_v, x0_r : std_logic;
    signal x0_d : integer;

    signal y0_v, y0_r : std_logic;
    signal y0_d : integer;

    signal z0_v, z0_r : std_logic;
    signal z0_d : integer;

begin
    adder_0: entity bjourne_pl.adder
        port map (
            clk => clk,
            nrst => nrst,

            u0_v => x0_v,
            u0_d => x0_d,
            u0_r => x0_r,

            u1_v => y0_v,
            u1_d => y0_d,
            u1_r => y0_r,

            d0_v => z0_v,
            d0_d => z0_d,
            d0_r => z0_r
        );
    process
        variable line0 : line;

        variable x_ds : integer_vector(0 to 3) := (3, 4, 9, 5);
        variable y_ds : integer_vector(0 to 3) := (10, 15, 19, 6);
        variable x_i : integer := 0;
        variable y_i : integer := 0;

    begin
        write(line0, string'("    "));
        write(line0, string'("x0: r v   D"));
        write(line0, string'(" "));
        write(line0, string'("y0: r v   D"));
        write(line0, string'(" "));
        write(line0, string'("z0: r v   D"));
        writeline(output, line0);

        clk <= '0';
        nrst <= '0';

        x0_v <= '0';
        y0_v <= '0';
        z0_r <= '0';

        tick(clk);

        nrst <= '1';

        for i in 0 to 50 loop
            tick(clk);
            write_ports(i, (x0_r, y0_r, z0_r),
                           (x0_v, y0_v, z0_v),
                           (x0_d, y0_d, z0_d));

            if (x0_r = '1') and (x_i < x_ds'length) then
                x0_v <= '1';
                x0_d <= x_ds(x_i);
                x_i := x_i + 1;
            end if;
            if (y0_r = '1') and (y_i < y_ds'length) then
                y0_v <= '1';
                y0_d <= y_ds(y_i);
                y_i := y_i + 1;
            end if;
        end loop;
        assert false report "all tests passed" severity note;
        wait;
    end process;
end architecture;
