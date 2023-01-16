-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use bjourne.types.all;

package io is
    procedure write_arr(x : integer_vector);
    procedure write_arr(x : real_vector);
    procedure write_arr(x : real_array2d_t);
end package io;
package body io is
    procedure write_arr(x : integer_vector) is
        variable line0 : line;
    begin
        for n in x'range loop
            write(line0, x(n), right, 5);
            write(line0, string'(" "));
        end loop;
        writeline(output, line0);
    end procedure;
    procedure write_arr(x : real_vector) is
        variable line0 : line;
    begin
        for n in x'range loop
            write(line0, to_string(x(n), string'("%6.2f")), right, 7);
            write(line0, string'(" "));
        end loop;
        writeline(output, line0);
    end procedure;
    procedure write_arr(x : real_array2d_t) is
    begin
        for n in x'range loop
            write_arr(x(n));
        end loop;
    end procedure;
end io;
