-- Copyright (C) 2023 Björn A. Lindqvist <bjourne@gmail.com>
library bjourne;
library ieee;
use ieee.float_pkg.all;
use ieee.numeric_std.all;

package types is
    type real_array2d_t is array(natural range<>) of real_vector;
    type int_array2d_t is array(natural range<>) of integer_vector;
end package;
